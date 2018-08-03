/**
 * Created by alexcomu on 04/05/17.
 */

import { debounce } from 'lodash'

export default ['$scope','$http','$sce','UserSearchFactory', '$rootScope', function ($scope, $http, $sce, UserSearchFactory, $rootScope) {
    
    $scope.search_factory = UserSearchFactory
    $scope.results_count = undefined
    $scope.results = [];
    
    $scope.search_debounced = debounce($scope.search_factory.search.bind($scope.search_factory.search), 500)

    $rootScope.$on('user.search.results', (event, results)=>{
        $scope.results = results['data']['result']
        $scope.results_count = results['data']['results_count']
        $scope.is_last_members_label = $scope.search_factory.search_filter === ''
    })
    
    $rootScope.$on('user.search.error', (event,data)=>{
        $scope.is_last_members_label = false;
        $scope.results = []
    })

    $scope.highlight = function(text, search) {
        if (!search) {return $sce.trustAsHtml(text);}
        return $sce.trustAsHtml(text.replace(new RegExp(search, 'gi'), '<span class="text-red bold">$&</span>'));
    };

    $scope.clearAll = () => { $scope.results = []; $scope.search_factory.search_filter = ''}
    
    // $scope.tag_template = (tags) => '<div class="tag-tooltip">'+tags.reduce( (acc, tag) => acc+`<span><strong>#</strong>${tag.name}</span><span>&nbsp;&nbsp;</span>`, '')+'</div>'
    $scope.tag_template = (tags) => tags.reduce((acc,tag)=>acc+`<span><strong>#</strong>${tag.name}</span><span>&nbsp;&nbsp;</span>`, '')
    
}]



















