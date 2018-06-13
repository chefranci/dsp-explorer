import json
import logging

logger = logging.getLogger(__name__)

from dashboard.models import User, Profile, Tag
import datetime

from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.parsers import JSONParser, MultiPartParser, FileUploadParser
from connectors.insight.connector import InsightConnectorV10 as Insight


class questions(APIView):

    parser_classes = (MultiPartParser, JSONParser)
    questions = []

    def get(self, request, action=None):

        entity_name = request.query_params.get('entity_name', None)
        entity_id = request.query_params.get('entity_id', None)

        # Request for signup questions
        not request.user.is_authenticated and not action and self.signup_questions(request)
        # Request for edit profile
        request.user.is_authenticated and action == 'profileedit' and self.edit_profile_questions(request)
        # Request for chatbot
        action == 'chatbot' and self.chatbot_question(request)
        # Feedback
        entity_name and entity_id and self.feedback_questions(request, entity_name, entity_id)

        return Response({'questions': self.questions})

    def post(self, request, action=None):
        '''

        :param request:
        :param action:
        :return:
            200 code for success
            403 if there is an error + {'error': [Error description]}
        '''

        try:
            # Send Chatbot Feedback to Insight
            if action == 'chatbot':
                response = Insight.feedback(
                    temp_id=request.data.get('temp_id', None),
                    crm_id=request.user.profile.crm_id,
                    feedback=request.data.get('feedback', None),
                )
            # Update User
            not action and self.update_user(request)

        except Exception as e:
            Response(data={'error': 'error send feedback'}, status=403)

        return Response()

    def feedback_questions(self, request, entity_name, entity_id):
        self.questions = [
            {
                "type": 'question',
                "temp_id": entity_id,
                "question": "How much you lile the " + entity_name + " on this page?",
                "text": "Click on the star to rate from 1 to 5",
                "actions": {'type': 'stars', 'amount': 5}
            },
        ]

    def signup_questions(self, request):
        self.questions = [
            self.make('register', 'message', 'Signup', value='Signup to Openmaker Explorer'),
            self.make('name', 'name', 'Who are you?'),
            self.make('gender', 'select', 'What is your gender?',
                      options=({'value': 'male', 'label': 'Male'}, {'value': 'female', 'label': 'Female'}, {'value': 'other', 'label': 'Does it matter?'})
                      ),
            self.make('birthdate', 'date', 'What is your birthdate?', max=str((datetime.datetime.now()-datetime.timedelta(days=16*365)).strftime('%Y/%m/%d'))),
            self.make('city', 'city', 'What is your city?'),
            self.make('occupation', 'text', 'What is your occupation?'),
            self.make('activity-question', 'activity-question', 'What is your activity?'),
            self.make('tags', 'multi_select', 'Choose 3 tags', options=[x.name for x in Tag.objects.all()]),
            self.make('signup', 'signup', 'Your login information', apicall='/api/v1.4/signup/'),
            self.make('sugnup_end', 'success', 'Thank you', value='Check your inbox for a confirmation email'),
        ]

    def chatbot_question(self, request):

        try:
            # or '145489262'
            crm_id = request.user.profile.crm_id
            response = Insight.questions(crm_ids=[crm_id])
            if response.status_code < 205:
                res_dict = response.json()
                questions = res_dict['users'][0]['questions']
                type = res_dict['users'][0]['feedback_type']
                self.questions = [self.map_questions(q, type) for q in questions]

        except Exception as e:
            print(e)
            self.questions = None

    def edit_profile_questions(self, request):

        user = request.user
        profile = request.user.profile
        questions = [
            self.make('name', 'name', 'What is your name?', value=[user.first_name, user.last_name]),
            self.make('gender', 'select', 'What is your gender?',
                      options=({'value': 'male', 'label': 'Male'}, {'value': 'female', 'label': 'Female'}, {'value': 'other', 'label': 'Does it matter?'})
                      ),
            self.make('occupation', 'text', 'What is your occupation?'),
            self.make('birthdate', 'date', 'What is your birthdate?',
                      max=str((datetime.datetime.now()-datetime.timedelta(days=16*365)).strftime('%Y/%m/%d')),
                      value=profile.birthdate.strftime('%Y/%m/%d'),
                      ),
            self.make('city', 'city', 'What is your city?', value={'city': profile.city, 'place': {}}),
            self.make('tags', 'multi_select', 'Choose 3 tags',
                      options=[x.name for x in Tag.objects.all()],
                      value=[x.name for x in profile.tags.all()],
                      ),
            self.make('activity-question', 'activity-question', 'What is your activity?',
                      value={
                          "domain": profile.domain.split(","),
                          "area": profile.area.split(","),
                          "technology": profile.technology.split(","),
                          "skills": profile.skills.split(",")
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

        self.questions = questions + [self.make('edit_end', 'success', 'Profile updated'), ]


    def map_questions(self, question, feedback_type='disagree_notsure_agree'):
        if feedback_type == 'disagree_notsure_agree':
            question['actions'] = {
                'type': 'buttons',
                'options':
                    [
                        {'value': 'agree', 'label': 'Agree'},
                        {'value': 'disagree', 'label': 'Disagree'},
                        {'value': 'notsure', 'label': 'Not Sure'}
                    ]
            }
            return self.make(name='', type='question', **question)

    def make(self, name, type, label='', **kwargs):
        question = {'name': name, 'type': type, 'label': label}
        for key, arg in kwargs.items():
            question[key] = arg
        return question

    def update_user(self, request):
        user = request.user
        profile = request.user.profile

        try:
            # User
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)

            # Profile
            profile.city = request.data.get('city', profile.city)
            profile.place = json.loads(request.data.get('place', profile.place))
            profile.birthdate = request.data.get('birthdate', profile.birthdate)
            profile.occupation = request.data.get('occupation', profile.occupation)
            profile.statement = request.data.get('statement', profile.statement)

            # Activity
            profile.domain = request.data.get('domain', profile.domain)
            profile.area = request.data.get('area', profile.area)
            profile.technology = request.data.get('technology', profile.technology)
            profile.skills = request.data.get('skills', profile.skills)

            # Profile Extra
            profile.tags_create_or_update(request.data.get('tags', None), clear=True)
            profile.picture_set_or_update(request.data.get('picture', None))

            user.save()
            profile.save()

        except Exception as error:
            return Response(data={'error': error}, status=403)

