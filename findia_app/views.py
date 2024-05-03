import json

import google.generativeai as genai
import pandas as pd
from django.contrib.auth.decorators import login_required
from django.core.serializers import serialize
from django.db.models import Sum
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render, reverse
from django.views.decorators.csrf import csrf_exempt

from .forms import MovementForm
from .models import Movement, ChatBot

from .forms import CreditForm
from .models import Credit

import json
from django.views.decorators.http import require_http_methods


genai.configure(api_key="AIzaSyDu-j3lqMXNaeZEiMSWTfRrssUDi7WQ-ow")


@login_required
def ask_question(request):
    if request.method == "POST":
        text = request.POST.get("text")
        user = request.user

        with open('findia_app/base_chat.txt', 'r') as file:
            base = file.read().strip()
        print("este es un text", base)
        movements = Movement.objects.filter(user=user)
        movements_json = serialize('json', movements)
        movements_data = json.loads(movements_json)

        type_mapping = {'I': 'Income', 'C': 'Cost'}
        modified_movements = []

        for item in movements_data:
            fields = item['fields']
            modified_movement = {
                'type': type_mapping.get(fields['type'], 'Unknown'),
                'value': fields['value'],
                'description': fields['description'],
                'date': fields['date']
            }
            modified_movements.append(modified_movement)

        movements_text = json.dumps(modified_movements)
        text = base + movements_text + " Responde este mensaje " + text
        print(text)

        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(text)

        ChatBot.objects.create(text_input=text, gemini_output=response.text, user=user)

        response_data = {
            "text": response.text
        }

        return JsonResponse({"data": response_data})
    else:
        return HttpResponseRedirect(reverse("chat"))


@login_required
def chat(request):
    user = request.user
    chats = ChatBot.objects.filter(user=user)
    return render(request, "chat.html", {"chats": chats})


@login_required
def list_movements(request):
    movements = Movement.objects.filter(user=request.user)
    movement_type = request.GET.get('type')

    if movement_type:
        movements = movements.filter(type=movement_type)

    total_ingresos = Movement.objects.filter(user=request.user, type='I').aggregate(Sum('value'))['value__sum'] or 0
    print(total_ingresos)
    total_gastos = Movement.objects.filter(user=request.user, type='C').aggregate(Sum('value'))['value__sum'] or 0

    context = {
        'movements': movements,
        'total_ingresos': total_ingresos,
        'total_gastos': total_gastos,
    }

    return render(request, 'movements/list.html', context)


@login_required
def create_movement(request):
    if request.method == 'POST':
        form = MovementForm(request.POST)
        if form.is_valid():
            movement = form.save(commit=False)
            movement.user = request.user
            movement.save()
            return redirect('list_movements')
    else:
        form = MovementForm()
    return render(request, 'movements/create.html', {'form': form})


@login_required
def edit_movement(request, pk):
    movement = Movement.objects.get(pk=pk)
    if request.method == 'POST':
        form = MovementForm(request.POST, instance=movement)
        if form.is_valid():
            form.save()
            return redirect('list_movements')
    else:
        form = MovementForm(instance=movement)
    return render(request, 'movements/edit.html', {'form': form})


@login_required
def delete_movement(request, pk):
    movement = Movement.objects.get(pk=pk)
    movement.delete()
    return redirect('list_movements')


@login_required
def create_credit(request):
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            credit = form.save(commit=False)
            credit.user = request.user
            credit.save()
            return redirect('list_credits')
    else:
        form = CreditForm()
    return render(request, 'credits/create.html', {'form': form})

@login_required
def list_credits(request):
    credits = Credit.objects.filter(user=request.user)
    return render(request, 'movements/list.html', {'credits': credits})


@login_required
def edit_credit(request, pk):
    credit = Credit.objects.get(pk=pk)
    if request.method == 'POST':
        form = CreditForm(request.POST, instance=credit)
        if form.is_valid():
            form.save()
            return redirect('list_credits')
    else:
        form = CreditForm(instance=credit)
    return render(request, 'credits/edit.html', {'form': form})

@login_required
def delete_credit(request, pk):
    credit = Credit.objects.get(pk=pk)
    credit.delete()
    return redirect('list_credits')


def credit_details(request, pk):
    credit = Credit.objects.get(pk=pk)
    monthly_payment = calculate_monthly_payment(credit.principal, credit.interest_rate, credit.term)
    payment_schedule_json = calculate_loan_payment_schedule(credit.principal, credit.term,
                                                            credit.interest_rate / 100 / 12, monthly_payment)

    return JsonResponse({
        'principal': credit.principal,
        'interestRate': credit.interest_rate,
        'term': credit.term,
        'monthlyPayment': monthly_payment,
        'paymentSchedule': payment_schedule_json
    })

@csrf_exempt
def calculate_credit(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        principal = float(data['principal'])
        interestRate = float(data['interestRate']) / 100
        term = int(data['term'])

        # Calcula el pago mensual
        monthly_rate = interestRate / 12
        monthly_payment = (principal * monthly_rate) / (1 - (1 + monthly_rate) ** (-term))

        return JsonResponse({'monthlyPayment': round(monthly_payment, 2)})

    return JsonResponse({'error': 'Invalid method'}, status=405)

def calculate_monthly_payment(PV, annual_interest_rate, n):
    """
    Calculate the fixed monthly payment for a loan.
    Parameters:
    - PV: Present Value or principal of the loan
    - annual_interest_rate: Annual interest rate in percentage
    - n: Total number of payments (loan term in months)
    Returns:
    - The fixed monthly payment amount
    """
    monthly_interest_rate = (annual_interest_rate / 100)/12

    discount_factor = (1 + monthly_interest_rate) ** -n

    payment = PV * monthly_interest_rate / (1 - discount_factor)
    payment = round(payment, 2)
    return payment


def calculate_loan_payment_schedule(loan_amount, total_periods, monthly_interest_rate, monthly_payment):
    """
    Calculate the loan payment schedule for a fixed payment loan with variable interest and principal
    components each month until the loan is paid off.

    Parameters:
    - loan_amount: The initial amount of the loan.
    - total_periods: The total number of payment periods.
    - monthly_interest_rate: The monthly interest rate as a decimal.
    - monthly_payment: The fixed amount to be paid each month.

    Returns:
    - A DataFrame with the payment schedule.
    """
    payment_schedule = pd.DataFrame({
        'Cuota No': range(1, total_periods + 1),
        'Valor cuota mensual': [monthly_payment] * total_periods,
        'Parte de la cuota que se convierte en abono a capital': [0] * total_periods,
        'Parte de la cuota que se convierte en abono a intereses': [0] * total_periods,
        'Saldo del crédito (capital) después del pago': [loan_amount] * total_periods
    })

    for i in range(total_periods):
        interest_payment = payment_schedule.at[
                               i, 'Saldo del crédito (capital) después del pago'] * monthly_interest_rate
        principal_payment = monthly_payment - interest_payment
        loan_balance = payment_schedule.at[i, 'Saldo del crédito (capital) después del pago'] - principal_payment
        payment_schedule.at[i, 'Parte de la cuota que se convierte en abono a intereses'] = interest_payment
        payment_schedule.at[i, 'Parte de la cuota que se convierte en abono a capital'] = principal_payment
        if i + 1 < total_periods:
            payment_schedule.at[i + 1, 'Saldo del crédito (capital) después del pago'] = loan_balance

    payment_schedule.at[total_periods - 1, 'Saldo del crédito (capital) después del pago'] = 0

    payment_schedule_json = payment_schedule.to_json(orient="records")
    return payment_schedule_json
