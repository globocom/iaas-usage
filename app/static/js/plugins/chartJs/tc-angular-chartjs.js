/**
 * Copyright 2015 Carl Craig
 * tc-angular-chartjs is dual licensed with the Apache-2.0 or MIT license.
 */

(function () {
  'use strict';
  angular
    .module( 'tc.chartjs', [] )
    .directive( 'tcChartjs', TcChartjs )
    .directive( 'tcChartjsLine', TcChartjsLine )
    .directive( 'tcChartjsBar', TcChartjsBar )
    .directive( 'tcChartjsRadar', TcChartjsRadar )
    .directive( 'tcChartjsPolararea', TcChartjsPolararea )
    .directive( 'tcChartjsPie', TcChartjsPie )
    .directive( 'tcChartjsDoughnut', TcChartjsDoughnut )
    .directive( 'tcChartjsLegend', TcChartjsLegend )
    .factory( 'TcChartjsFactory', TcChartjsFactory );

  function TcChartjs( TcChartjsFactory ) {
    return new TcChartjsFactory();
  }

  function TcChartjsLine( TcChartjsFactory ) {
    return new TcChartjsFactory( 'line' );
  }

  function TcChartjsBar( TcChartjsFactory ) {
    return new TcChartjsFactory( 'bar' );
  }

  function TcChartjsRadar( TcChartjsFactory ) {
    return new TcChartjsFactory( 'radar' );
  }

  function TcChartjsPolararea( TcChartjsFactory ) {
    return new TcChartjsFactory( 'polararea' );
  }

  function TcChartjsPie( TcChartjsFactory ) {
    return new TcChartjsFactory( 'pie' );
  }

  function TcChartjsDoughnut( TcChartjsFactory ) {
    return new TcChartjsFactory( 'doughnut' );
  }

  function TcChartjsFactory() {

    return function ( chartType ) {

      return {
        restrict: 'A',
        scope: {
          data: '=chartData',
          options: '=chartOptions',
          type: '@chartType',
          legend: '=?chartLegend',
          chart: '=?chart',
          click: '&chartClick',
          responsive: "=",
        },
        link: link
      };

      function link( $scope, $elem, $attrs ) {

        var ctx = $elem[0].getContext( '2d' );
        var chart = new Chart( ctx );
        var chartObj;
        var showLegend = false;
        var autoLegend = false;
        var exposeChart = false;
        var legendElem = null;

        for ( var attr in $attrs ) {
          if ( attr === 'chartLegend' ) {
            showLegend = true;
          } else if ( attr === 'chart' ) {
            exposeChart = true;
          } else if ( attr === 'autoLegend' ) {
            autoLegend = true;
          }
        }

        $scope.$on('$destroy', function() {
          if ( chartObj && typeof chartObj.destroy === 'function' ) {
            chartObj.destroy();
          }
        });

        if ($scope.click) {
          $elem[0].onclick = function (evt) {
            var segment;

            if (chartObj.getSegmentsAtEvent !== undefined) {
              segment = chartObj.getSegmentsAtEvent(evt);
            } else if (chartObj.getPointsAtEvent !== undefined) {
              segment = chartObj.getPointsAtEvent(evt);
            } else if (chartObj.getBarsAtEvent !== undefined) {
              segment = chartObj.getBarsAtEvent(evt);
            }

            $scope.click({data: segment, event: evt});
          };
        }

        $scope.$watch(
          'data',
          function ( value ) {

            if ( value ) {
              if ( chartObj && typeof chartObj.destroy === 'function' ) {
                chartObj.destroy();
              }
              if ( chartType ) {
                chartObj = chart[ cleanChartName( chartType ) ]( $scope.data, $scope.options );
              } else if ($scope.type) {
                chartObj = chart[ cleanChartName( $scope.type ) ]( $scope.data, $scope.options );
              } else {
                throw 'Error creating chart: Chart type required.';
              }

              if ( showLegend ) {
                $scope.legend = chartObj.generateLegend();
              }

              if ( autoLegend ) {
                if ( legendElem ) {
                  legendElem.remove();
                }
                angular.element($elem[0]).after( chartObj.generateLegend() );
                legendElem = angular.element($elem[0] ).next();
              }

              if ( exposeChart ) {
                $scope.chart = chartObj;
              }
              chartObj.resize();
            }

          },
          true
        );
      }

      function cleanChartName( type ) {
        var typeLowerCase = type.toLowerCase();
        switch ( typeLowerCase ) {
          case 'line':
            return 'Line';
          case 'bar':
            return 'Bar';
          case 'radar':
            return 'Radar';
          case 'polararea':
            return 'PolarArea';
          case 'pie':
            return 'Pie';
          case 'doughnut':
            return 'Doughnut';
          default:
            return type;
        }
      }

    };
  }

  function TcChartjsLegend() {

    return {
      restrict: 'A',
      scope: {
        legend: '=?chartLegend'
      },
      link: link
    };

    function link( $scope, $elem ) {

      $scope.$watch(
        'legend',
        function ( value ) {

          if ( value ) {
            $elem.html( value );
          }

        },
        true
      );
    }
  }

})();