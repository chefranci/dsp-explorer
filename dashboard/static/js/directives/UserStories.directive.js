import * as _ from 'lodash'

let template = `
    <div class="row">
        <div class="col-md-12">
            <h2><strong class="text-red">User Stories</strong></h2>
        </div>
        
        <div class="col-md-3" ng-repeat="story in stories">
            <div class="card margin-bottom-20">
                <a href="{$ story.link $}" target="_blank">
                    <div class="card-image" style="border-bottom:solid 1px rgba(160, 160, 160, 0.2);">
                        <img style="min-width:100%;" src="{$ story.image $}" class="img-responsive"alt="image">
                    </div>
                    <div class="card-content text-center">
                        <!--<h5>{{ feed.title|truncatechars:40 }}</h5>-->
                        <h5 ng-bind-html="story.title.rendered" ></h5>
                    </div>
                    <div class="card-action">
                        <p ng-bind-html="story.excerpt.rendered"></p>
                    </div>
                </a>
            </div>
        </div>
    </div>
`

export default [function(){
    
    return {
        template:template,
        scope: [],
        controller : ['$scope','$http', function($scope, $http){
            
            $scope.stories = []
            
            let openmaker_country = ['it', 'es', 'sk', 'uk']
            let openmaker_suffix = 'openmaker.eu'
            let api_suffix = 'wp-json/wp/v2'
            
            _.each(openmaker_country, country =>{
                let url = `http://${country}.${openmaker_suffix}/${api_suffix}/posts?_embed=true`
                $http.get(url).then(
                    res => {
                        res.data[0].image =
                            _.get(res, "data[0]['_embedded']['wp:featuredmedia'][0].source_url") ||
                            '/static/images/openmaker-logo.svg'
                        $scope.stories.push(res.data[0])
                        console.log(res)
                    }
                    ,
                    err => console.log('Error : ', err)
                )
            })
            
            console.log('stories : ',  $scope.stories)
            
        }]
    }
  
}]