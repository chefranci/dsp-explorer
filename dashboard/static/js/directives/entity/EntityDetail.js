import * as _ from 'lodash'
import * as d3 from 'd3';

let template = `
    <div class="entity--{$ entity $}">
   
        <div class="col-md-8 col-md-offset-1 entity-content">

            <!--Header With title and actions-->
            <div class="col-md-12 margin-bottom-1-perc">
                <h1 style="text-transform: uppercase">
                    <span>{$ entityname $}</span>
                    <span class="pull-right">
                        <bookmark-button entityname="{$ entityname $}" entityid="{$ entityid $}"></bookmark-button>
                        <interest-button entityname="{$ entityname $}" entityid="{$ entityid $}"></interest-button>
                    </span>
                <h1>
            </div>
            
            <!--Content-->
            <div class="col-md-12">
            
                <!--Loader-->
                <entity-loading
                    loading="!entity && !nodata"
                    loaded="entity"
                    nodata="nodata"
                    entityname="{$ entityname $}"
                ></entity-loading>
            
                <!-- Enitiy details -->
                <div  ng-if="entity !== null">
                    <div>
                        <h2 class="text--{$ entityname $}">{$ entity.title $}</h2>
                        <br>
                        <p ng-if="entity.lenght == 0">Loading data</p>
                        <p style="font-size:150%;">{$ entity.full_text $}</p>
                    </div>
                    <br>
                    <entity-interested entityname="{$ entityname $}" entityid="{$ entityid $}"></entity-interested>
                </div>
                
            </div>

        </div>

        <!--Sidebar-->
        <div class="col-md-3 entity-sidebar" style="background:#bbb;">
            <div ng-repeat="slider_name in slider_list" style="margin-top:5%;">
                <entity-carousel entityname="{$ slider_name $}"></entity-carousel>
            </div>
        </div>
        
    </div>
`

export default [function(){
    return {
        template:template,
        scope: {
            entityname: '@',
            entityid : '@',
            slider: '@'
        },
        controller : ['$scope', '$http', 'toastr', '$rootScope', '$timeout', function($scope, $http, toastr, $rootScope, $timeout) {
            let url = ''

            $scope.entity = null
            $scope.nodata = false
            
            $scope.slider_list = $scope.slider ? $scope.slider.split('-').filter(x => x): []
            
            $scope.get_data = (url) => {
                $http.get(url).then(res => {
                    $scope.entity = res.data.result[0] || null
                    $scope.nodata = $scope.entity.length === 0
                })
            }
            
            // MOCK
            $scope.get_data = (url)=>{
                $timeout(1500).then(()=>{
                    $scope.entity = {
                        title: 'asdasd',
                        full_text: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Duis et gravida libero, ut sagittis erat. Nulla ornare velit in ante tempus, in faucibus purus ornare. In et purus tincidunt, venenatis felis at, molestie urna. Mauris ornare dignissim libero at ornare. Proin ligula massa, rutrum quis arcu a, sodales porta nulla. Aliquam mauris odio, blandit ut lacus non, lobortis posuere elit. Proin varius urna ac nunc venenatis, quis lobortis turpis blandit. Suspendisse vel massa ornare, tempor lacus tincidunt, bibendum lorem. Curabitur lacinia, erat vitae luctus tempor, velit mi venenatis nunc, a auctor odio purus ac dolor. Vestibulum at lacus leo. Morbi purus ligula, suscipit non vestibulum et, semper ac eros. Suspendisse mollis justo in nisi mattis molestie. Ut ut turpis et sapien dictum bibendum ut ut lorem. In id mollis ligula, eu rutrum nibh. Donec quis diam sed mi pretium varius. Aenean varius erat libero, id auctor magna efficitur et.\n'
                    }
                })
            }
            // ENDMOCK
            
            $scope.get_data('/api/v1.4/' + $scope.entityname + '/details/' + $scope.entityid + '/')
    
        }]
    }
}]



