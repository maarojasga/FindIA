from django.shortcuts import render, redirect
from .models import Movement, ChatBot
from .forms import MovementForm
from django.db.models import Sum
from django.shortcuts import render, reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
import google.generativeai as genai

# Create your views here.
# add here to your generated API key
genai.configure(api_key="AIzaSyDu-j3lqMXNaeZEiMSWTfRrssUDi7WQ-ow")


@login_required
def ask_question(request):
    if request.method == "POST":
        text = request.POST.get("text")
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(text)
        user = request.user
        ChatBot.objects.create(text_input=text, gemini_output=response.text, user=user)
        # Extract necessary data from response
        response_data = {
            "text": response.text,  # Assuming response.text contains the relevant response data
            # Add other relevant data from response if needed
        }
        return JsonResponse({"data": response_data})
    else:
        return HttpResponseRedirect(
            reverse("chat")
        )  # Redirect to chat page for GET requests


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

    # Asegúrate de que los valores 'ingreso' y 'gasto' están correctamente escritos como en tus modelos
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