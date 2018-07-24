import * as _ from 'lodash'
let template = /*html*/`
    <div class="container entity-list">
        <div class="row ">
        
            <!--Entity heading-->
            <div class="entity-list__title entity-heading col-md-12 col-sm-12">
                <div class="row">
                    <h1 class="col-md-9 col-sm-9 col-sm-offset-0">
                       <span class="entity-detail__title">
           
                            <span ng-if="entityname !== 'projects'" >{$ entityname $}</span>
                            <span ng-if="entityname === 'projects'" >Projects / <span class="text-red">Challenges</span></span>
                       </span>
                       
                       <span ng-if="$root.authorization>=10 && entityname === 'projects'">
                            <a href="/profile/project/"><i class="fa fa-plus-circle text-{$ entityname $}"></i></a>
                       </span>
                       
                       <span class="pull-right">
                            <bookmarked-stripe-toggler entityname="{$ entityname $}"></bookmarked-stripe-toggler>
                       </span>
                       
                   <h1>
                </div>
            </div>
        
            <!--Left content-->
            <div class="col-md-9 col-sm-9 col-sm-offset-0 entity-content" >
                <div class="row">
                    
                    <div class="col-md-12">
    
                        <entity-loading
                            loading="entities.data.length==0 && !nodata"
                            error="nodata"
                            entityname="{$ entityname $}"
                        ></entity-loading>
                        
                    </div>
    
                    <div ng-if="entities.data.length > 0" >
                    
                        <bookmarked-stripe entityname="{$ entityname $}"></bookmarked-stripe>
                    
                        <!--Entity list-->
                        <div
                            class="col-lg-4 col-md-6 col-sm-12 col-xs-12 "
                            ng-repeat="entity in entities.data"
                            style="margin-bottom:1%; margin-top: 1%;"
                        >
                            <div class="entity-list__box">
                                <entity-detail
                                    entity="entity"
                                    entityname="{$ entityname=='projects' && entity.hasOwnProperty('company')? 'challenges' : entityname $}"
                                    entityid="{$ entity.link_id || entity.id $}"
                                    preview="true"
                                ></entity-detail>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="row">
                    <div class="col-md-12">
                        <simple-pagination
                                prevfunction="search_factory.prev_page"
                                nextfunction="search_factory.next_page"
                                currentpagenumber="search_factory.page"
                                maxpagenumber="search_factory.max_page"
                        ></simple-pagination>
                    </div>
                </div>
            </div>
        
            <!--Right sidebar-->
            <div class="col-md-3" >
                <entity-sidebar slider="{$ slider $}" entityname="{$ entityname $}"></entity-sidebar>
            </div>
            
        </div>

    </div>
`

export default [function(){
    return {
        template:template,
        scope: {
            profileid : '=',
            entityname : '@',
            slider : '@'
        },
        controller : ['$scope', '$http', 'EntityProvider', async function($scope, $http, EntityProvider) {
            $scope.entities = EntityProvider.make($scope.entityname)
            $scope.nodata = !$scope.entities.get()
        }]
    }
}]





