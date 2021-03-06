let _ = require('lodash')
let $ = require('jquery')


let template = `
    <div ng-if="questions" class="profile-questions">
        <div
            ng-repeat="question in questions"
            class=" col-lg-4 col-md-6 col-sm-12 col-xs-12 margin-bottom-1-perc profile-question"
            style="position: relative"
            ng-init="question.is_action=false; question.is_edit=false;"
            ng-click="question.is_action=!question.is_action"
        >
            <div
                class="profile-question__inner background-white"
                ng-class="{'profile-question--edit': question.is_edit}"
            >
                <div
                    class="profile-question__actions"
                    ng-show="question.is_action"
                    ng-if="!question.is_edit"
                >
                    <h3
                        class="far fa-fw text-red background-white pointer"
                        ng-class="{'fa-eye': !question.is_private, 'fa-eye-slash':question.is_private }"
                        ng-if="!question.feedbacks[1] && !question.is_edit"
                        style=" position: absolute; top:0%; right:10%;"
                        ng-click="toggle_show(question); $event.stopPropagation();"
                        uib-tooltip-html="'Show/hide yor answer to other people'"
                    ></h3>

                    <h3
                        class="fas fa-fw fa-edit text-red background-white pointer"
                        style="position: absolute; bottom:10%; right:10%;"
                        ng-click="question.is_edit = !question.is_edit;"
                        ng-show="!question.is_edit && !(is_my_profile && question.feedbacks[1]);"
                        uib-tooltip-html="'Edit your answer'"
                    ></h3>
                    
                </div>
                
                <div style="margin: 1%;">
                
                    <h4 class="text-brown">{$ question.question $}</h4>
                    <p>{$ question.question_text $}</p>
                    <hr>
                    
                    <!--OTHER USER-->
                    <p ng-if="!is_my_profile" class="text-brown">
                        <strong>{$ profile.data.user.first_name $}'s answer:&nbsp;</strong>&nbsp;&nbsp;{$ question.feedbacks[0].label $}
                    </p>
                    
                    <!--ME-->
                    <p ng-if="!is_my_profile" class="text-red">
                        <strong>Your answer:&nbsp;</strong>
                            <span>&nbsp;&nbsp;{$ question.feedbacks[1].label || 'You have not answered yet...' $}</span>
                    </p>
                    <p ng-if="is_my_profile" class="text-red">
                        <strong>Your answer:&nbsp;</strong>&nbsp;&nbsp;{$ question.feedbacks[0].label $}
                    </p>
                    
                    <button
                        ng-show="!question.is_edit && !is_my_profile && !question.feedbacks[1]"
                        style="position: absolute; bottom:10%; right:10%;"
                        class="btn btn-danger btn-small pointer"
                        ng-click="question.is_edit = !question.is_edit"
                    >Answer this question!</button>

                </div>
                
                <div ng-show="question.is_edit">
                
                    <h3
                        class="far fa-fw fa-times-circle text-red background-white pointer"
                        
                        style="position: absolute; top:0%; right:5%;"
                        ng-click="toggle_edit(question)"
                        uib-tooltip-html="'Exit from edit mode'"
                    ></h3>
                    
                    <div class="profile-question__answers">
                        <div ng-repeat="(act, k) in question.answers" style="padding:2px; z-index:10000;" >
                            <button
                                class="btn btn-danger pull-left capitalize pointer"
                                ng-click="edit_question(question, k)"
                            >{$ act $}</button>
                        </div>
                    </div>
                    
                </div>
                
                
            </div>
            
            
        </div>
    </div>
`

let profile_question_directive =
{
    template:template,
    scope: {
        profile : '='
    },
    controller: ['$scope', '$rootScope', '$http', '$timeout', 'EntityProvider', function($scope, $rootScope, $http, $timeout, EntityProvider){
        
        $scope.profileid = _.get($rootScope, 'page_info.options.profile_id')
        $scope.questions = null
        $scope.wizard_id = $scope.$id;
        $scope.is_my_profile = $scope.profileid == _.get($rootScope, 'user.profile')
        
        $scope.wizard_name = 'wizard.'+$scope.wizard_id;
        
        $scope.get = ()=>{
            $scope.profileid &&
            $http.get(`/api/v1.4/questions/profile?profile_id=${$scope.profileid}`)
                .then((r)=>{$scope.questions = r.data.questions || null;  console.log($scope.questions);})
        }
        
        $scope.get()
        $rootScope.$on('authorization.refresh', $scope.get)
        $rootScope.$on('chatbot.next', $scope.get)
        
        $scope.toggle_show = async(q)=> {
            q.is_private = !q.is_private
            let res= await $http.post('/api/v1.4/questions/chatbot/', q)
            //$scope.get()
            
        }
        
        $scope.edit_question = async(question, feedback)=>{
            let q = {...question}
            q.feedback = feedback
            let res= await $http.post('/api/v1.4/questions/chatbot/', q)
            $scope.get()
        }
    
        $scope.toggle_edit = (question)=>{
            question.is_edit = !question.is_edit
        }

    }]
}

export default [()=>profile_question_directive]

