from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.template.loader import get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings


from .models import Chat, Persona
from chatbot.models import Chat

import openai

#Recuerda a la hora de subir esto a GitHub sacar la key y ponerla directamente de ubuntu 
openai_api_key = ''
openai.api_key = openai_api_key

e_mensaje = []

def configuracion(request):
    user = request.user
    persona = Persona.objects.filter(user=request.user).latest('tn_peso')

    if request.method == 'POST':
        fecha_nacimiento = request.POST['fecha_nacimiento']
        genero = request.POST['genero']
        altura = request.POST['altura']

        # Actualizar los campos en el objeto persona
        persona.fecha_nacimiento = fecha_nacimiento
        persona.genero = genero
        persona.altura = altura
        persona.save()

        return redirect('configuracion')

    context = {
        'user': user,
        'persona': persona,
    }
    return render(request, 'configuracion.html', context)

def pesos(request):
    personas = Persona.objects.filter(user=request.user).order_by('tn_peso')

    if request.method == 'POST':
        nuevo_peso = float(request.POST['nuevo_peso'])
        peso_anterior = personas.last().peso if personas.count() > 1 else 0

        nueva_persona = Persona.objects.create(
            user=request.user,
            fecha_nacimiento=personas.last().fecha_nacimiento if personas.exists() else None,
            genero=personas.last().genero if personas.exists() else None,
            peso=nuevo_peso,
            altura=personas.last().altura if personas.exists() else None,
            tn_peso=timezone.now(),
        )

        subida_o_bajada = "Subida" if nuevo_peso > peso_anterior else "Bajada"
        diferencia = abs(nuevo_peso - peso_anterior)

        # Redirigir a la vista 'pesos' después de procesar el formulario
        return redirect('pesos')

    context = {
        'persona': personas.last(),
        'subida_o_bajada': "N/A",
        'diferencia': None,
        'pesos': personas,
    }

    # Calcular la diferencia de peso y la subida o bajada desde la penúltima medición
    if personas.count() > 1:
        peso_anterior = personas[len(personas) - 2].peso
        peso_actual = context['persona'].peso
        diferencia = peso_actual - peso_anterior
        if diferencia > 0:
            context['subida_o_bajada'] = "Subida"
        elif diferencia < 0:
            context['subida_o_bajada'] = "Bajada"
        context['diferencia'] = abs(diferencia)

    # Mostrar mensaje si no ha habido cambios de peso desde la última medición
    if context['diferencia'] == 0:
        context['subida_o_bajada'] = "Sin cambios"

    return render(request, 'pesos.html', context)

def index (mail):
    print(e_mensaje)
    template = get_template('correo.html')
    content = template.render({"e_mensaje": e_mensaje})
    email = EmailMultiAlternatives(
    'Aqui esta lo que pediste',
    'Aqui esta lo que pediste',
    settings.EMAIL_HOST_USER,
    [mail],
    )

    email.attach_alternative(content, 'text/html')
    email.send()

    return mail

def inicio(request):
    return render(request, 'inicio.html')

def respuesta(request):
    return render(request, 'respuesta.hmtl')

def limitacion_msj(o_limi, res_otro_limi, o_lugar, res_otro_lugar):
    limitaciones = o_limi
    if limitaciones == "Otro":
        limitaciones = res_otro_limi
    lugar_limitacion = o_lugar
    if lugar_limitacion == "Otro":
        lugar_limitacion = res_otro_lugar
    limitacion = f"Si tengo limitaciones, esta es un " +limitaciones+ " en el " +lugar_limitacion
    return limitacion

def dieta_msj(usuario, genero, edad, altura, peso, gustan, nogustan, restricciones_alimenticias):
    mensaje = f"Hola soy {usuario}, de sexo {genero}, tengo {edad} años, mido {altura} y peso {peso}, "
    if gustan == [''] and nogustan == [''] and restricciones_alimenticias == ['']: #No gusta, No nogusta, No limitaciones
        mensaje = mensaje + "No tengo preferencias alimentarias, me gusta todo en general y nininguna restriccion alimenticias que me impida comer algun tipo de alimento "
    elif gustan != [''] and nogustan == [''] and restricciones_alimenticias == ['']: #Si gusta, No nogusta, No limitaciones
        mensaje = mensaje + f"Mis prefetencias alimnentacias son que me gustan las {gustan}. No tengo ninugna restriccion alimenticias " 
    elif gustan == [''] and nogustan != [''] and restricciones_alimenticias == ['']: #No gusta, Si nogusta, No limitaciones
        mensaje = mensaje + f"Mis prefetencias alimnentacias son que no me gustan las {nogustan}. No tengo ninugna restriccion alimenticias "
    elif gustan == [''] and nogustan == [''] and restricciones_alimenticias != ['']: #No gusta, No nogusta, Si limitaciones
        mensaje = mensaje + f"No tengo preferencia alimentarias, pero tengo las siguiente restricciones alimenticias {restricciones_alimenticias} "    
    elif gustan != [''] and nogustan != [''] and restricciones_alimenticias == ['']: #Si gusta, Si nogusta, No limitaciones
        mensaje = mensaje + f"Mis prefetencias alimnentacias son que me gustan las {gustan} y no me gustan {nogustan}. No tengo ninugna restriccion alimenticias "
    elif gustan != [''] and nogustan == [''] and restricciones_alimenticias != ['']: #Si gusta, No nogusta, Si limitaciones
        mensaje = mensaje + f"Mis prefetencias alimnentacias son que me gustan las {gustan}. Tengo las siguiente restricciones alimenticias {restricciones_alimenticias} "        
    elif gustan == [''] and nogustan != [''] and restricciones_alimenticias != ['']: #No gusta, Si nogusta, Si limitaciones
        mensaje = mensaje + f"Mis prefetencias alimnentacias son que no me gustan las {nogustan}. Tengo las siguiente restricciones alimenticias {restricciones_alimenticias} "
    elif gustan != [''] and nogustan != [''] and restricciones_alimenticias != ['']: #Si gusta, Si nogusta, Si limitaciones
        mensaje = mensaje + f"Mis prefencias alimentcias son que me gustan {gustan} y no me gustan {nogustan}, " \
                            f"y tengo las siguiente restricciones alimenticias {restricciones_alimenticias}, "          
    return mensaje

def formulario_dieta(request):
    global e_mensaje
    mail = request.POST.get('mail', '')
    if request.method == 'POST' and '@' in mail:
        index(mail)
        context = {'mail_sent': True}
        return render(request, 'inicio.html', context)
    if request.method == 'POST' and not '@' in mail:
        conversa = []
        gustan = request.POST.getlist('gustan[]', [])
        nogustan = request.POST.getlist('nogustan[]', [])
        restricciones_alimenticias = request.POST.getlist('restricciones_alimentarias[]', [])
        enfoque_dieta = request.POST.get('enfoque', '')
        #obtener datos de la base de datos
        usuario = User.objects.get(username=request.user)
        persona = Persona.objects.filter(user=request.user).latest('tn_peso')
        edad = (timezone.now().date()).year - persona.fecha_nacimiento.year
        mensaje = dieta_msj(usuario, persona.genero, edad, persona.altura, persona.peso, gustan, nogustan, restricciones_alimenticias)

        if enfoque_dieta == "ganancia_muscular":
            suplementos = request.POST.get('suplementos', '')
            #obtener datos de la base de datos
            conversa.append({"role": "system", "content": "Necesito que actues como un nutricionista con experiencia en ganancia muscular, necesito que realices una dieta completa para una persona que esta en proceso de ganar masa muscular detallada en kcal y otras informaciones, necesito que lo guies con una dieta para el dia y los suplementos que puede tomar si lo pide con un poco de informacion"})
            mensaje = mensaje + f"{suplementos} quiero uso de suplementos alimenticios"
            conversa.append({"role": "user", "content": mensaje})
            response = ask_openai(conversa)
            print(response)
            e_mensaje = response
            # Redirigir a otra vista después de enviar el formulario
            return render(request, 'respuesta.html', {'response': response})


        if enfoque_dieta == "perdida_peso":
            historial_alimentario = request.POST.get('historial_alimentario', '')
            habitos_alimenticio = request.POST.get('habitos_alimenticio', '')
            conversa.append({"role": "system", "content": "Necesito que actues como un nutricionista con experiencia en perdida de peso, necesito que realices una dieta completa para una persona que esta en proceso de perder peso detallada en kcal y otras informaciones, necesito que lo guies con una dieta que pueda hacer un dia"})
            mensaje = mensaje + f"me alimentaba de: {historial_alimentario}, " \
                                f"y me en cantidades y horarios {habitos_alimenticio}"
            conversa.append({"role": "user", "content": mensaje})
            response = ask_openai(conversa)
            print(response)
            e_mensaje = response
            # Redirigir a otra vista después de enviar el formulario
            return render(request, 'respuesta.html', {'response': response})

        if enfoque_dieta == "definicion":
            calorias_actuales = request.POST.get('calorias_actuales', '')
            porcentaje_proteina = request.POST.get('porcentaje_proteina', '')
            porcentaje_carbohidratos = request.POST.get('porcentaje_carbohidratos', '')
            porcentaje_grasas = request.POST.get('porcentaje_grasas', '')
            uso_suplementos = request.POST.get('uso_suplementos', '')
            conversa.append({"role": "system", "content": "Necesito que actues como un nutricionista con experiencia en definicion muscular, necesito que realices una dieta completa para una persona que esta en proceso de definicion muscular detallada en kcal y otras informaciones, necesito que lo guies con una dieta que pueda hacer un dia y los suplementos que puede tomar con un poco de informacion"})
            mensaje = mensaje + f"actualmente consumo {calorias_actuales}, " \
                                f"las cuales se reparten en {porcentaje_proteina}% de proteina, {porcentaje_carbohidratos}% de carbohidratos y {porcentaje_grasas}% de grasa, " \
                                f"y {uso_suplementos} consumo suplementos. "
            conversa.append({"role": "user", "content": mensaje})
            response = ask_openai(conversa)
            print(response)
            e_mensaje = response
            # Redirigir a otra vista después de enviar el formulario
            return render(request, 'respuesta.html', {'response': response})

        if enfoque_dieta == "rehabilitacion":
            habitos_alimenticios = request.POST.get('habitos_alimenticios', '')
            conversa.append({"role": "system", "content": "Necesito que actues como un nutricionista con en recuperacion, necesito que realices una dieta completa para una persona que esta en proceso de recuperacion detallada en kcal y otras informaciones, necesito que lo guies con una dieta que pueda hacer un dia"})
            mensaje = mensaje + f"me alimento de: {habitos_alimenticios}"
            conversa.append({"role": "user", "content": mensaje})
            response = ask_openai(conversa)
            print(response)
            e_mensaje = response
            # Redirigir a otra vista después de enviar el formulario
            return render(request, 'respuesta.html', {'response': response})
    return render(request, 'formulario_dieta.html')

def formulario_r(request):
    mail = request.POST.get('mail', '')
    if request.method == 'POST' and '@' in mail:
        index(mail)
        context = {'mail_sent': True}
        return render(request, 'inicio.html', context)
    if request.method == 'POST' and not '@' in mail:
        conversa = []
        # Obtener los valores de los campos del formulario
        diagnostico_medico = request.POST.get('diagnostico_medico', '')
        historial_medico = request.POST.get('historial_medico', '')
        evaluacion_fisica = request.POST.get('evaluacion_fisica', '')
        historial_actividad_fisica = request.POST.get('historial_actividad_fisica', '')
        objetivo_rehabilitacion = request.POST.get('objetivo_rehabilitacion', '')
        recursos_disponibles = request.POST.get('recursos_disponibles', '')
        disponibilidad_dias = request.POST.get('disponibilidad_d', '')
        disponibilidad_horas = request.POST.get('disponibilidad_h', '')
        restriccion_limitaciones = request.POST.get('restriccion_limitaciones', '')
        condiciones_entorno = request.POST.get('condiciones_entorno', '')
        #obtener datos de la base de datos
        usuario = User.objects.get(username=request.user)
        persona = Persona.objects.filter(user=request.user).latest('tn_peso')
        edad = (timezone.now().date()).year - persona.fecha_nacimiento.year
        # Crear el mensaje con los valores obtenidos
        conversa.append({"role": "system", "content": "Necesito que actues como un kinesiólogo con experiencia en rehabilitacion de pacientes no me digas que eres kinesiologo, realizando una pauta de rehabilitacion para que el usuraio siga"})
        mensaje = f"Hola soy {usuario}, de sexo {persona.genero}, tengo {edad} años, mido {persona.altura} y peso {persona.peso}, " \
                  f"Diagnóstico médico: {diagnostico_medico}, " \
                  f"Este es mi historial medico: {historial_medico}, " \
                  f"Este es mi evaluacion fisica: {evaluacion_fisica}, " \
                  f"Mi historial de actividad fisica antes de la lesion: {historial_actividad_fisica}, " \
                  f"Mi objetivo de esta rehabilitacion es: {objetivo_rehabilitacion}, " \
                  f"Cuento con estos recursos para la rehabilitacion: {recursos_disponibles}, " \
                  f"Tengo una disponibilidad de {disponibilidad_horas} hrs por dia, " \
                  f"Tengo estas limitaciones: {restriccion_limitaciones}, " \
                  f"Y mis condiciones de entorno son: {condiciones_entorno}" 
        conversa.append({"role": "user", "content": mensaje})
        # Enviar el mensaje a chatbot y obtener la respuesta
        response = ask_openai(conversa)
        print(response)
        global e_mensaje
        e_mensaje = response


        # Redirigir a otra vista después de enviar el formulario
        return render(request, 'respuesta.html', {'response': response})

    return render(request, 'formulario_r.html')

def formulario_p(request):
    mail = request.POST.get('mail', '')
    if request.method == 'POST' and '@' in mail:
        index(mail)
        context = {'mail_sent': True}
        return render(request, 'inicio.html', context)
    if request.method == 'POST' and not '@' in mail:
        conversa = []
        # Obtener los valores de los campos del formulario
        diagnostico_medico = request.POST.get('diagnostico_medico_p', '')
        nivel_actividad_fisica = request.POST.get('nivel_actividad_fisica_p', '')
        perdida_p = request.POST.get('perdida_peso_objetivo', '')
        disponibilidad_dias = request.POST.get('disponibilidad_d', '')
        disponibilidad_horas = request.POST.get('disponibilidad_h', '')
        #obtener datos de la base de datos
        usuario = User.objects.get(username=request.user)
        persona = Persona.objects.filter(user=request.user).latest('tn_peso')
        edad = (timezone.now().date()).year - persona.fecha_nacimiento.year
        imc_p = (persona.peso/((persona.altura**2)/10000))
        print(imc_p)
        # Crear el mensaje con los valores obtenidos
        conversa.append({"role": "system", "content": "Necesito que actues como un personal trainer con experiencia en perdida de peso, necesito que hagas una rutina de ejercicios completa para perder peso, describiendo el dia y el tiempo que demorara esto"})
        
        if diagnostico_medico == "No":
            limitacion = f"No tengo limitaciones"
        elif diagnostico_medico == "Si":
            limitacion = limitacion_msj(request.POST.get('diagnostico_medico', ''), request.POST.get('otro_limitacion', ''), request.POST.get('lugares_limitacion', ''), request.POST.get('otro_lugar', ''))
        
        mensaje = f"Hola soy {usuario}, de sexo {persona.genero}, tengo {edad} años, mido {persona.altura} y actualmente peso {persona.peso}, " \
                  f"{limitacion}, " \
                  f"Tengo un imc de: {imc_p}, " \
                  f"Quiero perder {perdida_p}, " \
                  f"Nivel de Actividad Física: {nivel_actividad_fisica}, " \
                  f"Tengo una disponibilidad de {disponibilidad_dias} dias a las semana, con un duracion estimada de {disponibilidad_horas} hrs por dia"
        conversa.append({"role": "user", "content": mensaje})
        # Enviar el mensaje a chatbot y obtener la respuesta
        response = ask_openai(conversa)
        print(response)
        global e_mensaje
        e_mensaje = response


        # Redirigir a otra vista después de enviar el formulario
        return render(request, 'respuesta.html', {'response': response})
    return render(request, 'formulario_p.html')

def formulario_d(request):
    mail = request.POST.get('mail', '')
    if request.method == 'POST' and '@' in mail:
        index(mail)
        context = {'mail_sent': True}
        return render(request, 'inicio.html', context)
    if request.method == 'POST' and not '@' in mail:
        conversa = []
        # Obtener los valores de los campos del formulario
        diagnostico_medico = request.POST.get('diagnostico_medico_d', '')
        nivel_actividad_fisica = request.POST.get('nivel_actividad_fisica_d', '')
        nivel_experiencia_entrenamiento = request.POST.get('nivel_experiencia_entrenamiento_d', '')
        obj_definicion_muscular = request.POST.get('obj_definicion_d', '')
        disponibilidad_dias = request.POST.get('disponibilidad_dias', '')
        disponibilidad_horas = request.POST.get('disponibilidad_horas', '')
        #obtener datos de la base de datos
        usuario = User.objects.get(username=request.user)
        persona = Persona.objects.filter(user=request.user).latest('tn_peso')
        edad = (timezone.now().date()).year - persona.fecha_nacimiento.year
        # Crear el mensaje con los valores obtenidos
        conversa.append({"role": "system", "content": "Necesito que actues como un personal trainer con experiencia en definicion muscular, necesito que hagas una rutina de ejercicios completa para definir musculos, describiendo el dia y las zonas que se trabajan en se dia, y el tiempo que demorara esto"})
        
        if diagnostico_medico == "No":
            limitacion = f"No tengo limitaciones"
        elif diagnostico_medico == "Si":
            limitacion = limitacion_msj(request.POST.get('diagnostico_medico', ''), request.POST.get('otro_limitacion', ''), request.POST.get('lugares_limitacion', ''), request.POST.get('otro_lugar', ''))

        mensaje = f"Hola soy {usuario}, de sexo {persona.genero}, tengo {edad} años, mido {persona.altura} y peso {persona.peso}, " \
                  f"{limitacion} " \
                  f"Nivel de Actividad Física: {nivel_actividad_fisica}, " \
                  f"Nivel de Experiencia en Entrenamiento: {nivel_experiencia_entrenamiento}, " \
                  f"Objetivo de Definicion muscular: {obj_definicion_muscular} % de grasa corporal, " \
                  f"Tengo una disponibilidad de {disponibilidad_dias} dias a las semana, con un duracion estimada de {disponibilidad_horas} hrs por dia"
        conversa.append({"role": "user", "content": mensaje})
        # Enviar el mensaje a chatbot y obtener la respuesta
        response = ask_openai(conversa)
        print(response)
        global e_mensaje
        e_mensaje = response


        # Redirigir a otra vista después de enviar el formulario
        return render(request, 'respuesta.html', {'response': response})
    return render(request, 'formulario_d.html')

def formulario(request):
    mail = request.POST.get('mail', '')
    if request.method == 'POST' and '@' in mail:
        index(mail)
        context = {'mail_sent': True}
        return render(request, 'inicio.html', context)
    if request.method == 'POST' and not '@' in mail:
        conversa = []
        # Obtener los valores de los campos del formulario
        diagnostico_medico = request.POST.get('tiene_limitaciones', '')
        nivel_actividad_fisica = request.POST.get('nivel_actividad_fisica_m', '')
        nivel_experiencia_entrenamiento = request.POST.get('nivel_experiencia_entrenamiento_m', '')
        obj_ganancia_muscular = request.POST.get('obj_ganancia_m', '')
        disponibilidad_dias = request.POST.get('disponibilidad_d', '')
        disponibilidad_horas = request.POST.get('disponibilidad_h', '')
        #obtener datos de la base de datos
        usuario = User.objects.get(username=request.user)
        persona = Persona.objects.filter(user=request.user).latest('tn_peso')
        edad = (timezone.now().date()).year - persona.fecha_nacimiento.year

        # Crear el mensaje con los valores obtenidos
        conversa.append({"role": "system", "content": "Necesito que actues como un personal trainer con experiencia en ganancia muscular, necesito que hagas una rutina de ejercicios completa para ganar masa muscular, describiendo el dia y las zonas que se trabajan en se dia, y el tiempo que demorara esto"})
        if diagnostico_medico == "No":
            limitacion = f"No tengo limitaciones"
        elif diagnostico_medico == "Si":
            limitacion = limitacion_msj(request.POST.get('diagnostico_medico', ''), request.POST.get('otro_limitacion', ''), request.POST.get('lugares_limitacion', ''), request.POST.get('otro_lugar', ''))
              
        mensaje = f"Hola soy {usuario}, de sexo {persona.genero}, tengo {edad} años, mido {persona.altura} y peso {persona.peso}, " \
                  f"{limitacion}, " \
                  f"Mi nivel de Actividad Física es {nivel_actividad_fisica}, " \
                  f"Mi nivel de Experiencia en Entrenamiento es {nivel_experiencia_entrenamiento}, " \
                  f"Objetivo de Ganancia Muscular: {obj_ganancia_muscular} Kg, " \
                  f"Tengo una disponibilidad de {disponibilidad_dias} dias a las semana, con un duracion estimada de {disponibilidad_horas} hrs por dia"
        conversa.append({"role": "user", "content": mensaje})
        # Enviar el mensaje a chatbot y obtener la respuesta
        response = ask_openai(conversa)
        print(response)
        global e_mensaje
        e_mensaje = response
        # Redirigir a otra vista después de enviar el formulario
        return render(request, 'respuesta.html', {'response': response})


    # Si no es una solicitud POST, renderiza el formulario
    return render(request, 'formulario.html')

def casillas(request):
    return render(request, 'casillas.html')

def ask_openai(conversa):
    print(conversa) #supervision de contexto de la aplicacion
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=conversa,
        temperature = 0.9
    )
    answer = response.choices[0].message.content.strip()
    return answer

def conversation_list(request):
    if request.user.is_authenticated:
        chats = Chat.objects.filter(user=request.user, reset_conversation=True)
        return render(request, 'conversation_list.html', {'chats': chats})
    else:
        return redirect('login')

def chatbot(request):
    if request.user.is_authenticated:
        user_chats = Chat.objects.filter(user=request.user)
        chats = user_chats.filter(reset_conversation=True)
    else:
        chats = None

    if request.method == 'POST':
        reset_conversation = False
        reset_conversation_id = request.POST.get('reset_conversation_id')
        print(reset_conversation_id)
        if reset_conversation_id:
            try:
                chat = user_chats.get(id=reset_conversation_id)
                previous_chat_id = int(reset_conversation_id) - 1
                if previous_chat_id >= 1:
                    previous_chat = user_chats.get(id=previous_chat_id)
                    conversa = eval(previous_chat.conversa)
                    request.session['conversa'] = conversa
                    temp=1 
                    request.session['temp'] = temp
                else:
                    conversa = []
                reset_conversation = True
            except Chat.DoesNotExist:
                conversa = []
        else:
            try:
                latest_chat = user_chats.latest('created_at')
                conversa_str = latest_chat.conversa
            except Chat.DoesNotExist:
                conversa_str = None

            conversa = eval(conversa_str) if conversa_str else []
            if conversa == []:
                temp = request.session.get('temp', [])
                if temp==1:
                    conversa = request.session.get('conversa', [])
                    temp=0
                    request.session['temp'] = temp
                else:
                    conversa.append({"role": "system", "content": "eres un excelente ayudante"})

        message = request.POST.get('message')
        
        reset_conversation = False
        if message == "secreta":
            reset_conversation = True

        
        if (reset_conversation == False) and (message != None):
            conversa.append({"role": "user", "content": message})
            response = ask_openai(conversa)
            conversa.append({"role": "assistant", "content": response})
            print(conversa)  # Saber qué mueve la aplicación por detrás
            chat = Chat(
                user=request.user, message=message, response=response,
                conversa=conversa, reset_conversation=reset_conversation,
                created_at=timezone.now()
            )
            chat.save()
            return JsonResponse({'message': message, 'response': response})
        
        if reset_conversation:
            conversa = []  # Reiniciar la conversación
            chat = Chat(
            user=request.user,
            conversa=conversa, reset_conversation=reset_conversation,
            created_at=timezone.now()
            )
            chat.save()

    return render(request, 'chatbot.html', {'chats': chats})

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('inicio')
        else:
            error_message = 'Usuario o clave inválida'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        fecha_nacimiento = request.POST['date_of_birth']
        genero = request.POST['gender']
        peso = request.POST['peso']
        altura = request.POST['altura']

        if password1 == password2:
            try:
                user = User.objects.create_user(username, email, password1)
                user.save()
                auth.login(request, user)
                persona = Persona(user=user, fecha_nacimiento=fecha_nacimiento, genero=genero, peso=peso, altura=altura)
                persona.save()
                return redirect('inicio')
            except:
                error_message = 'Cuenta ya creada'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Las claves no son iguales'
            return render(request, 'register.html', {'error_message': error_message})
    return render(request, 'register.html')

def logout(request):
    auth.logout(request)
    return redirect('inicio')