import json
import logging

logger = logging.getLogger(__name__)

from dashboard.models import User, Profile, Tag
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
from connectors.insight.connector import InsightConnectorV10 as Insight
import pprint

class questions(APIView):

    parser_classes = (MultiPartParser, JSONParser)
    questions = []

    def get(self, request, action=None):
        '''

        :param request:
        :param action:
        :return:
            200 code for success + question list
            403 if there is an error + {'error': [Error description]}
        '''

        entity_name = request.query_params.get('entity_name', None)
        entity_id = request.query_params.get('entity_id', None)
        temp_id = request.query_params.get('entity_temp_id', None)
        profile_id = request.query_params.get('profile_id', None)

        if request.user.is_authenticated:
            # Request for edit profile
            action == 'profileedit' and self.edit_profile_questions(request)
            # Request for chatbot
            action == 'chatbot' and self.chatbot_question(request)
            # Feedback
            entity_name and temp_id and self.feedback_questions(request, entity_name, temp_id)
            action == 'profile' and self.profile_questions(request, profile_id)

        else:
            # Request for signup questions
            not action and self.signup_questions(request)
            # Chatbot for visitors
            action == 'chatbot' and self.visitor_questions(request)

        return Response({'questions': self.questions})

    def post(self, request, action=None):
        '''

        :param request:
        :param action:
        :return:
            200 code for success
            403 if there is an error + {'error': [Error description]}
        '''

        temp_id = request.data.get('temp_id', None)
        question_id = request.data.get('question_id', None)
        feedback = request.data.get('feedback', None)
        is_private = request.data.get('is_private', None)

        try:
            # Send Chatbot Feedback to Insight
            if action == 'chatbot' and request.user.is_authenticated:
                crm_id = request.user.profile.crm_id

                # Entity Feedback
                if temp_id is not None:
                    return Response(Insight.feedback(temp_id=temp_id, crm_id=crm_id, feedback=feedback))
                # Change Question privacy
                elif feedback is None and is_private is not None:
                    return Response(Insight.question_privacy(crm_id=crm_id, question_ids=[question_id], is_private=is_private))
                # Send answer to question
                elif question_id is not None:
                    return Response(Insight.question_feedback(crm_id=crm_id, question_id=question_id, answer_id=feedback))

            # Update User
            not action and self.update_user(request)

        except Exception as e:
            print(' ###################################################')
            print(e)
            return Response(data={'error': str(e) }, status=403)
        return Response()

    def feedback_questions(self, request, entity_name, entity_id):
        '''

        :param request:
        :param entity_name:
        :param entity_id:
        :return: void - it's only modify self.questions
        '''
        self.questions = [] \
            if entity_name in ['challenges', 'projects'] \
            else [
                self.question('rate_entity', entity_name=entity_name, entity_id=entity_id, first_name=request.user.first_name),
                self.question('rate_bye', entity_name=entity_name, first_name=request.user.first_name)
            ]

    def visitor_questions(self, request):
        self.questions = [
            self.question('signup_proposal'),
            self.question('signup_proposal_2')
        ]

    def profile_questions(self, request, profile_id):
        '''

        :param request:
        :param profile_id:
        :return: void - it's only modify self.questions
        '''


        try:
            crm_ids = [
                Profile.objects.filter(pk=request.user.profile.id).first().crm_id,
                Profile.objects.filter(pk=profile_id).first().crm_id
            ]
            are_the_same_profiles = crm_ids[0] == crm_ids[1]

            # Get feedbacks from insight
            feedbacks = Insight.profile_questions(crm_ids)

            # check if the response from insight is ok
            if len(feedbacks) > 0:
                logged_user_feedbacks = feedbacks[0]['feedbacks']['questions']
                target_user_feedbacks = feedbacks[1]['feedbacks']['questions']

                # if the target user does not have questions stop the execution
                if len(target_user_feedbacks) < 1:
                    self.questions = []
                    return
                # Create list of merged questions
                else:
                    self.questions = self.merge_question_and_feedback(target_user_feedbacks)
                    if not are_the_same_profiles:
                        self.questions = self.merge_question_and_feedback(logged_user_feedbacks, self.questions)
                        self.questions = [v for k, v in self.questions.items() if not v['is_private']]
            else:
                self.questions = []

        except KeyboardInterrupt as e:
            print(e)

    def merge_question_and_feedback(self, fedbacks=None, questions=None):
        '''

        :param fedbacks:
        :param questions:
        :return: void - it's only modify self.questions
        '''
        from itertools import groupby
        # Get feedbacks
        user_fedbacks = fedbacks

        f_sorted = sorted(user_fedbacks, key=lambda k: k['q_id'])
        grouped = groupby(f_sorted, lambda x: x['q_id'])
        groups = {k: list(v).pop() for k, v in grouped}

        # Get questions
        ids = list(groups.keys())
        user_questions = questions or Insight.question_contents(ids).json()

        # For every question adds a feedback property containing a list of the answers of both the users
        for k, feedback in groups.items():
            id = str(feedback['q_id'])
            if id in user_questions:
                fb = [{'label': feedback['answer_value'], 'value': feedback['answer_id']}]
                user_questions[id]['feedbacks'] = fb if not 'feedbacks' in user_questions[id] else user_questions[id]['feedbacks'] + fb
                if questions is None:
                    user_questions[id]['is_private'] = feedback['is_private']

        return user_questions

    def signup_questions(self, request):
        '''

        :param request:
        :return: void - it's only modify self.questions
        '''
        self.questions = [
            self.question('signup_welcome'),
            self.question('user_full_name'),
            self.question('user_gender'),
            self.question('user_birthdate'),
            self.question('user_city'),
            self.question('user_occupation'),
            self.question('activity_question_1'),
            self.question('activity_question_2'),
            self.question('activity_question_3'),
            self.question('activity_question_4'),
            #self.question('user_tags'),
            self.question('user_signup_data'),
            self.question('signup_bye'),
        ]

    def chatbot_question(self, request):
        '''

        :param request:
        :return: void - it's only modify self.questions
        '''

        entity_name = request.query_params.get('entity_name', None)
        entity_id = request.query_params.get('entity_id', None)
        temp_id = request.query_params.get('entity_temp_id', None)
        profile_id = request.query_params.get('profile_id', None)

        try:
            welcome = self.question('welcome', first_name=request.user.first_name)
            bye = self.question('nice_talking', first_name=request.user.first_name)

            crm_id = request.user.profile.crm_id
            response = Insight.questions(crm_ids=[crm_id], amount=10)

            if response.status_code < 205:
                res_dict = response.json()
                questions = res_dict['users'][0]['questions'] \
                    if isinstance(res_dict['users'], dict) or isinstance(res_dict['users'], list) \
                    else []

                if len(questions) > 0:
                    self.questions = [welcome] + [self.map_remote_to_local_questions(q) for q in questions] + [bye]
                else:
                    self.questions = [self.question('no_questions', first_name=request.user.first_name)]
            else:
                print('[dashboard.questions.questions.chatbot_question] CHATBOT QUESTION insight response error')
                print(response)

        except Exception as e:
                print('[ERROR : dashboard.questions.questions.chatbot_question]')
                print(e)
                self.questions = self.questions = [self.question('no_questions', first_name=request.user.first_name)]

    def edit_profile_questions(self, request):
        '''

        :param request:
        :return: void - it's only modify self.questions
        '''
        user = request.user
        profile = request.user.profile
        sixteen_date = (datetime.datetime.now()-datetime.timedelta(days=16*365)).strftime('%Y/%m/%d')
        questions = [
            self.make('name', 'name', 'What is your name?', value=[user.first_name, user.last_name]),
            self.make('gender', 'select', 'What is your gender?',
                      options=({'value': 'male', 'label': 'Male'}, {'value': 'female', 'label': 'Female'}, {'value': 'other', 'label': 'Does it matter?'})
                      ),
            self.make('occupation', 'text', 'What is your occupation?'),
            self.make('birthdate', 'date', 'What is your birthdate?',
                      max=str(sixteen_date),
                      value=profile.birthdate.strftime('%Y/%m/%d') if profile.birthdate else sixteen_date,
                      ),
            self.make('city', 'city', 'What is your city?', value={'city': profile.city, 'place': {}}),
            # self.make('tags', 'multi_select', 'Choose 3 tags',
            #           options=[x.name for x in Tag.objects.all()],
            #           value=[x.name for x in profile.tags.all()],
            #           ),
            self.make('activity-question-1', 'activity-question-1', 'What is your activity?</br>(1 of 4)',
                      value={
                          "domain": [x['name'] for x in profile.activity('domain')],
                      }),
            self.make('activity-question-2', 'activity-question-2', 'What is your activity?</br>(2 of 4)',
                      value={
                          "area": [x['name'] for x in profile.activity('area')]
                      }
                      ),
            self.make('activity-question-3', 'activity-question-3', 'What is your activity?</br>(3 of 4)',
                      value={
                          "technology": [x['name'] for x in profile.activity('technology')],
                      }
                      ),
            self.make('activity-question-4', 'activity-question-4', 'What is your activity?</br>(4 of 4)',
                      value={
                          "skills": [x['name'] for x in profile.activity('skills')]
                      }
                      ),
            self.make('statement', 'textarea', 'Short description about you (optional)'),
            self.make('picture', 'imageupload', 'Upload you profile image (optional)',
                      value=profile.picture.url if profile.picture else None,
                      apicall='/api/v1.4/questions/',
                      emitevent='entity.change.all'
                      ),
        ]

        # Add Values
        for question in questions:
            question['value'] = question.get('value', None) \
                                or getattr(profile, question['name'], None) \
                                or getattr(user, question['name'], None)

            question['apicall'] = True

        self.questions = questions + [self.make('edit_end', 'success', 'Profile updated'), ]

    def map_remote_to_local_questions(self, question):
        '''

        :param question:
        :return: list of questions each added with 'options' key
        '''
        question['actions'] = {
            'type': 'buttons',
            'options': [{'label': k, 'value': v} for k, v in question['answers'].items()]
        }
        return self.make(name='', type='question', **question)

    def update_user(self, request):
        '''

        :param request:
        :return: SUCCESS : void ; ERROR : 403 response
        '''
        user = request.user
        profile = request.user.profile
        print('im on user update')

        city = request.data.get('city', profile.city)
        place = request.data.get('place', profile.place)

        # try:
        # User
        user.first_name = request.data.get('first_name', user.first_name)
        user.last_name = request.data.get('last_name', user.last_name)

        # Profile
        profile.city = city if not not city else profile.city
        profile.place = place if bool(place) else profile.palce

        profile.birthdate = request.data.get('birthdate', profile.birthdate)
        profile.occupation = request.data.get('occupation', profile.occupation)
        profile.statement = request.data.get('statement', profile.statement)
        profile.gender = request.data.get('gender', profile.gender)

        # Activity
        profile.activity('area', request.data.get('area', None))
        profile.activity('technology', request.data.get('technology', None))
        profile.activity('skills', request.data.get('skills', None))
        profile.activity('domain', request.data.get('domain', None))

        # Profile Extra
        #profile.tags_create_or_update(request.data.get('tags', None), clear=True)

        picture = request.data.get('picture', None)
        profile.picture_set_or_update(picture) if picture and len(picture) > 0 else None

        user.save()
        profile.save()

        try:
            party = profile.create_or_update_to_crm(profile.user)
            crm_id = party and party.get_crm_id()
            crm_id and Insight.notify_user_creation(crm_id)
        except Exception as e:
            logger.log('error', e)

    @classmethod
    def question(cls, question, **kwargs):
        '''
        Convenience method to easy build a question
        :param question: name of the question
        :param kwargs: a list of params needed to build the question (eg: if the text require the user name)
        :return: the requested question if exists else return None
        '''
        from dashboard.models import EntityProxy

        first_name = kwargs.get('first_name', '')
        entity_id = kwargs.get('entity_id', '')
        entity_name = kwargs.get('entity_name', '')

        static_questions = {
            'welcome': {
                'type': "question",
                'question': 'Hi, '+first_name+'!',
                'text': "Do you have time for some questions?",
                'actions': {'options': [{'label': 'yes, sure!'},  {'value': 'goto:last', 'label': 'no, thanks'}]}
            },
            'nice_talking': {
                'type': "question",
                'question': "Nice talking "+first_name+"!",
                'text': "Have a nice day",
                'actions': {'options': ['  Bye!  ']}
            },
            'no_questions': {
                'type': "question",
                'question': "I'm really busy right now "+first_name+"!",
                'text': "I will come back to you soon",
                'actions': {'options': ['  Bye!  ']}
            },
            'rate_entity': {
                "type": 'question',
                "temp_id": entity_id,
                "super_text": "Hi! " + first_name + "",
                "question": "Do you like the " + EntityProxy.singular_name(entity_name) + " on this page?",
                "text": "Click on the stars to rate from 1 to 5",
                "actions": {'type': 'stars', 'amount': 5}
            },
            'rate_bye': {
                'type': "question",
                'question': 'Thank you!, '+first_name+'!',
                'text': "Now i will be able to show you more interesting " + entity_name,
                'actions': {'options': ['  Thank you!  ']}
            },
            'signup_proposal': {
                'type': "question",
                'question': 'Hi visitor!',
                'text': "Do you know that signed users have access to more content than you?",
                'actions': {'options': ['Tell me more',  {'value': 'event:chatbot.close', 'label': 'I don\'t mind'}]}
            },
            'signup_proposal_2': {
                'type': "question",
                "super_text": 'You can view only 5 contents per day',
                'question': 'If you signup you will have full access to the site contents.' ,
                'text': "Do you Want to signup?",
                'actions': {'options': [{'value': 'event:question.modal.open', 'label': 'Yes'}, 'Not now' ]}
            },
        }

        form_questions = {
            'signup_welcome': cls.make('signup_welcome', 'message', 'Signup', value='Signup to Open Maker Explorer'),
            'user_full_name': cls.make('name', 'name', 'Who are you?'),
            'user_gender': cls.make('gender', 'select', 'What is your gender?',
                 options=({'value': 'male', 'label': 'Male'}, {'value': 'female', 'label': 'Female'}, {'value': 'other', 'label': 'Does it matter?'})
            ),
            'user_birthdate': cls.make('birthdate', 'date', 'What is your birthdate?',
                 max=str((datetime.datetime.now()-datetime.timedelta(days=16*365)).strftime('%Y/%m/%d'))
            ),
            'user_city': cls.make('city', 'city', 'What is your city?'),
            'user_occupation': cls.make('occupation', 'text', 'What is your occupation?'),
            'activity_question_1': cls.make('activity-question-1', 'activity-question-1', 'What is your activity? </br>(1 of 4)'),
            'activity_question_2': cls.make('activity-question-2', 'activity-question-2', 'What is your activity? </br>(2 of 4)'),
            'activity_question_3': cls.make('activity-question-3', 'activity-question-3', 'What is your activity? </br>(3 of 4)'),
            'activity_question_4': cls.make('activity-question-4', 'activity-question-4', 'What is your activity? </br>(4 of 4)'),
            'user_tags': cls.make('tags', 'multi_select', 'Choose 3 tags', options=[x.name for x in Tag.objects.all()]),
            'user_signup_data': cls.make('signup', 'signup', 'Your login information', apicall='/api/v1.4/signup/'),
            'signup_bye': cls.make('signup_end', 'success', 'Thank you', value='Check your inbox for a confirmation email'),
        }

        return static_questions.get(question, None) or form_questions.get(question, None)

    @classmethod
    def make(cls, name, type, label='', **kwargs):
        '''

        :param name:
        :param type:
        :param label:
        :param kwargs:
        :return:
        '''
        question = {'name': name, 'type': type, 'label': label}
        for key, arg in kwargs.items():
            question[key] = arg
        return question
