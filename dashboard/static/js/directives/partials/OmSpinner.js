export default [function(){
    return {
        template:`
            <div class="om_spinner">
                  <div class="bounce1"></div>
                  <div class="bounce2"></div>
                  <div class="bounce3"></div>
            </div>
            
            <style>
            
            .om_spinner {
              margin: 100px auto 0;
              width: 70px;
              text-align: center;
            }
            
            .om_spinner > div {
              width: 18px;
              height: 18px;
              background-color: #333;
            
              border-radius: 100%;
              display: inline-block;
              -webkit-animation: sk-bouncedelay 1.4s infinite ease-in-out both;
              animation: sk-bouncedelay 1.4s infinite ease-in-out both;
            }
            
            .om_spinner .bounce1 {
              -webkit-animation-delay: -0.32s;
              animation-delay: -0.32s;
            }
            
            .om_spinner .bounce2 {
              -webkit-animation-delay: -0.16s;
              animation-delay: -0.16s;
            }
            
            @-webkit-keyframes sk-bouncedelay {
              0%, 80%, 100% { -webkit-transform: scale(0) }
              40% { -webkit-transform: scale(1.0) }
            }
            
            @keyframes sk-bouncedelay {
              0%, 80%, 100% {
                -webkit-transform: scale(0);
                transform: scale(0);
              } 40% {
                -webkit-transform: scale(1.0);
                transform: scale(1.0);
              }
            }
            </style>
            
        `,
        scope: {
            entityname : '@',
            entityid : '@'
        },
        controller : ['$scope', '$http', '$rootScope', function($scope, $http, $rootScope){
            $scope.interested = false;
            // $scope.interest = (challenge) => $scope.interested = !$scope.interested
    
            // Build url
            let url = `/api/v1.4/interest/${$scope.entityname}/${$scope.entityid}/`
    
            // Change bookmarked button color
            const change_status = res => {
                if(res.status === 200){
                    $scope.interested = _.get(res, 'data.result.iaminterested', $scope.interested)
                    $rootScope.$emit('interested.new')
                }
            }
    
            // First check if is bookmarked
            $http.get(url).then(change_status)
    
            // Change bookmark on BE
            $scope.interest = () =>{ $http.post(url).then(change_status) }
            
        }]
    }
}]
