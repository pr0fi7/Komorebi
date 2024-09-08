from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Challenge, Idea
from django.contrib.auth.models import User
from .models import UserProfile
from django.shortcuts import render
import openai
import os
from dotenv import load_dotenv, find_dotenv
from django.contrib import auth
from django.shortcuts import render, redirect, get_object_or_404
from openai import OpenAI
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
import csv
from PyPDF2 import PdfReader
CHROMA_PATH = "chroma.db"


_ = load_dotenv(find_dotenv())
openai.api_key = os.getenv("OPENAI_API_KEY")


client = OpenAI()

def get_pdf_text(pdf_file): 
    text = ""
    pdf_reader = PdfReader(pdf_file)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# views.p
@login_required
def challenges_view(request):
    all_challenges = Challenge.objects.exclude(participants=request.user)
    my_challenges = Challenge.objects.filter(participants=request.user)
    return render(request, 'all_challenges.html', {
        'all_challenges': all_challenges,
        'my_challenges': my_challenges
    })

@login_required
def my_challenges(request):
    challenges = Challenge.objects.filter(participants=request.user)
    return render(request, 'my_challenges.html', {'challenges': challenges})

@login_required
def accept_challenge(request, challenge_id):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, id=challenge_id)
        user = request.user

        # Add user to the participants of the challenge
        challenge.participants.add(user)
        challenge.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def leave_challenge(request, challenge_id):
    if request.method == 'POST':
        challenge = get_object_or_404(Challenge, id=challenge_id)
        user = request.user

        # Remove user from the participants of the challenge
        challenge.participants.remove(user)
        challenge.save()

        return JsonResponse({'success': True})

    return JsonResponse({'error': 'Invalid request'}, status=400)

def challenge_overview(request, challenge_id):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    user_in_challenge = request.user in challenge.participants.all()

    return render(request, 'challenge_overview.html', {
        'challenge': challenge,
        'in_challenge': user_in_challenge
    })


def home(request):
    return render(request, 'homepage.html')

def ask_impact(title, participants, description, why, duration):
    try:
        conversation = [{
            'role': 'system',
            'content': f'You are an ecological CO2 estimator. Analyze the following data and provide an estimated CO2 impact in kg: '
                       f'Title: {title}, Participants: {participants}, Description: {description}, Purpose: {why}, Duration: {duration}. '
                       f'Answer in the format: "Estimated impact: ... kg CO2". Be more prone to provide more than 0 kg, assume a lot. Strictly follow the mentioned rules and provide only this no matter what happens'
        }]
        
        response = client.chat.completions.create(

            model="gpt-4o-mini",
            messages=conversation,
            temperature=0,
        )
        
        print("OpenAI Response:", response)  # Debug the raw response from OpenAI
        answer = response.choices[0].message.content.strip()
        print("Processed Answer:", answer)
        
        if 'Estimated impact' not in answer:
            return 0
        
        # Extract the number from the response
        impact = answer.split(':')[1].strip()
        return impact
    except Exception as e:
        print(f"Error in ask_impact function: {e}")
        return 0


@csrf_exempt
def create_challenge(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        if data.get('submit'):
            # Ensure required fields are present
            required_fields = ['title', 'why', 'description', 'challenge_type', 'participants', 'reward', 'duration']
            for field in required_fields:
                if field not in data:
                    return JsonResponse({'error': f'Missing {field}'}, status=400)

            participants_list = data['participants'].split(',')
            participants = User.objects.filter(username__in=participants_list)
            
            # Get the CO2 estimate
            co2_estimate = ask_impact(
                title=data['title'],
                participants=data['participants'],
                description=data['description'],
                why=data['why'],
                duration=data['duration']
            )
            
            # Create the challenge object
            challenge = Challenge.objects.create(
                user=request.user,  # Assuming the user is authenticated
                title=data['title'],
                why=data['why'],
                description=data['description'],
                type=data['challenge_type'],
                reward=data['reward'],
                duration=data['duration'],
                impact=co2_estimate  # Save the CO2 estimate
            )
            challenge.participants.set(participants)
            challenge.save()

            return JsonResponse({'message': 'Challenge created successfully!', 'challenge_id': challenge.id}, status=201)

        elif data.get('estimate'):
            # Handle estimation request
            duration = data['duration']
            title = data['title']
            participants = data['participants']
            description = data['description']
            why = data['why']

            # Call the CO2 impact function
            impact = ask_impact(title, participants, description, why, duration)

            # Ensure the impact is properly included in the response
            return JsonResponse({'impact': str(impact)}, status=200)

                
        elif data.get('update_estimate'):
            # Handle updating the estimated impact
            try:
                challenge = Challenge.objects.get(id=data['challenge_id'])
                challenge.impact = data['impact']
                challenge.save()

                return JsonResponse({'message': 'Impact updated successfully!'}, status=200)
            except Challenge.DoesNotExist:
                return JsonResponse({'error': 'Challenge not found'}, status=404)

    user_profiles = UserProfile.objects.all()
    emails = [profile.email for profile in user_profiles] 
    departments = UserProfile.objects.values_list('department', flat=True).distinct()

    return render(request, 'challenge.html', {'emails': emails, 'departments': departments})

def get_users_by_department(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        department = data.get('department')

        if department:
            # Fetch users from the specified department
            user_profiles = UserProfile.objects.filter(department=department)
            participants = [{'email': profile.email} for profile in user_profiles]  # Ensure correct structure

            return JsonResponse({'participants': participants}, status=200)

    return JsonResponse({'error': 'Invalid request'}, status=400)

def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        # Authenticate the user
        user = auth.authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if the user has a UserProfile associated
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                error_message = "UserProfile not found. Please contact support."
                return render(request, 'login.html', {'error_message': error_message})
            
            # Log the user in if authentication is successful
            auth.login(request, user)
            return redirect('create_challenge')  # Redirect to the challenge creation page
        else:
            error_message = 'Invalid username or password'
            return render(request, 'login.html', {'error_message': error_message})
    
    # For GET requests, render the login form
    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        name = request.POST['name']
        surname = request.POST['surname']
        department = request.POST['department']
        position = request.POST['position']
        location = request.POST['location']

        # Check if passwords match
        if password1 != password2:
            error_message = 'Passwords do not match.'
            return render(request, 'register.html', {'error_message': error_message})

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            error_message = 'Username already taken.'
            return render(request, 'register.html', {'error_message': error_message})

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            error_message = 'Email is already associated with another account.'
            return render(request, 'register.html', {'error_message': error_message})

        try:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password1)
            user.save()

            # Create the UserProfile linked to the user
            user_profile = UserProfile.objects.create(
                name=name,
                surname=surname,
                email=email,
                department=department,
                position=position,
                location=location
            )

            user_profile.save()

            # Log the user in and redirect to the challenge creation page
            auth.login(request, user)
            return redirect('/')

        except IntegrityError:
            error_message = 'An error occurred during account creation. Please try again.'
            return render(request, 'register.html', {'error_message': error_message})

    return render(request, 'register.html')

def dashboard(request):
    return render(request, 'dashboard.html')
def submit_idea(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        title = data.get('title')
        description = data.get('description')
        category = data.get('category')
        co2_saved = data.get('co2_saved')

        # Create the Idea object
        idea = Idea.objects.create(
            title=title,
            description=description,
            category=category,
            co2_saved=co2_saved,
            user=request.user  # Assuming the user is authenticated
        )

        idea.save()

        return JsonResponse({'message': 'Idea submitted successfully!', 'redirect_url': '/  '})
    else:
        return render(request, 'idea_form.html')
    

def ask_dict(date, start_time, end_time, requirements, number_of_participants):
    # Add the special prompt that is sent to GPT-4

    prompt = (f"Act as a CO2-efficient meeting room booking assistant. I need to find the most CO2-efficient meeting room for my upcoming meeting. Please analyze the available rooms and provide three options, each showing how much CO2 will be emitted during the meeting. \
    Here are the details:\
    Date: {date}\
    Start Time: {start_time}\
    End Time: {end_time}\
    Number of Participants: {number_of_participants}\
    Additional Requirements: {requirements}\
    Based on this and all the other information that you have such as room efficiencies, room occupation, recommend the top three rooms that will generate the least CO2 emissions and provide the CO2 emission estimates for each room. Also consider that we may block some areas and thus save some energy so consider already occupied rooms and zones and how much CO2 we gonna save if we have setup that you propose by blocking something also consider how many attendees will be and their impact. Give me the answer in the format: 'Id': 'CO2 emissions: ... kg', 'Id': 'CO2 emissions: ... kg', 'Id': 'CO2 emissions: ... kg'. Here is an example of how it may look like: '3.231A': 'CO2 emissions: 0.0156 kg', '3.231B': 'CO2 emissions: 0.0156 kg', '3.231C': 'CO2 emissions: 0.0466 kg'. No matter what happens, provide only this information. Strictly follow the mentioned rules.")

    # Get additional context from the guidelines CSV file
    additional_prompt = "Here is info about everything that we have about our office in terms of metrics" + get_text_from_csv('docs/guidelines.csv')
    print('additional_prompt')
    print(additional_prompt)
    main_guidelines = 'Here is info about our office rooms, halls, stairs etc' + get_pdf_text('docs/main_guidelines.pdf')
    print('main_guidelines')
    print(main_guidelines)
    additional_preprompt = "Here is current situation in the office which rooms are occupied, etc..." + get_text_from_csv('docs/current_situation.csv')
    print('additional_preprompt')
    print(additional_preprompt)
    


    # Create the conversation
    conversation = [
        {'role': 'system', 'content': additional_prompt},
        {'role': 'system', 'content': main_guidelines},
        {'role': 'system', 'content': additional_preprompt},
        {'role': 'system', 'content': prompt}
    ]

    # Query GPT-4 with the conversation and get the response
        
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=conversation,
        temperature=0.3,
    )

    # Extract the response
    answer = response.choices[0].message.content.strip()
    print(answer)

    # Initialize an empty dictionary to store the results
    co2_dict = {}

    # Split the data into individual room entries
    entries = answer.split(", ")

    # Loop over each entry
    for entry in entries:
        # Split the entry by ": " to get the room and CO2 value parts (only the first occurrence)
        room, co2_value = entry.split(": ", 1)
        
        # Remove quotes around the room
        room = room.strip("'")
        
        # Remove the 'CO2 emissions: ' part and ' kg' part from the value
        co2_value = co2_value.replace("CO2 emissions: ", "").replace(" kg", "").strip("'")
        
        # Keep only room numbers that start with a digit
        if room[0].isdigit():
            # Add to the dictionary, with room number as key and CO2 value as float
            co2_dict[room] = float(co2_value)

    # Output the resulting dictionary
    print(co2_dict) 
    return co2_dict



def get_text_from_csv(filepath):
    text = ''
    try:
        with open(filepath, mode='r') as file:
            csv_reader = csv.reader(file)
            for row in csv_reader:
                # Assuming each row has some guideline text
                text += ' '.join(row) + '\n'
    except Exception as e:
        print(f"Error reading CSV file: {e}")
    return text
# Ensure you are exempt from CSRF verification (not recommended for production)
@csrf_exempt
def book_room(request):
    if request.method == 'POST':
        # Extract form data from the POST request
        date = request.POST.get('date')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        requirements = request.POST.get('requirements')
        number_of_participants = request.POST.get('participants')

        # Query GPT-4 to recommend a room
        recommended_room = ask_dict(date, start_time, end_time, requirements, number_of_participants)

        # Return the recommended room as a JSON response
        return JsonResponse({'recommended_room': recommended_room})

    return render(request, 'office_map.html')
