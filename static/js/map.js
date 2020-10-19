anychart.onDocumentReady(function () {
    anychart.data.loadJsonFile(
      'https://cdn.anychart.com/samples/maps-point-maps-dot-maps/usa-biggest-cities/data.json',
      function (data) {
        var map = anychart.map(); // creates map chart

        map
          .unboundRegions()
          .enabled(true)
          .fill('#E1E1E1')
          .stroke('#D2D2D2');

        map
          .credits()
          .enabled(true)
          .url(
            'https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population'
          )
          .text(
            'Data source: https://en.wikipedia.org/wiki/List_of_United_States_cities_by_population'
          )
          .logoSrc('https://en.wikipedia.org/static/favicon/wikipedia.ico');

        map.geoData('anychart.maps.united_states_of_america');  // sets geodata

        // helper function to create several series
        var createSeries = function (name, data, color) {
          // sets marker series for airports
          var series = map.marker(data).name(name);
          series.legendItem({
            iconType: 'circle',
            iconFill: color,
            iconStroke: '2 #E1E1E1'
          });

          // sets Tooltip for series
          series
            .tooltip()
            .useHtml(true)
            .padding([8, 13, 10, 13])
            .title(false)
            .separator(false)
            .fontSize(14)
            .format(function () {
              return (
                '<span>' +
                this.getData('name')
              );
            });

          // sets settings for marker-airports series
          series
            .selectionMode('none')
            .stroke('2 #757575')
            .fill(color)
            .size(10)
            .labels(false)
            .type('circle');

          series.hovered().stroke('3 #616161').fill(color).size(15);
        };

        // creates Dataset from Sample data
        var citiesDataSet = anychart.data.set(data).mapAs();

        // creates 5 series, filtering the data by the amount of Fatalities
        createSeries(
          ' ',
          citiesDataSet.filter('size', filterFunction(100000, 200000)),
          '#80deea'
        );
        createSeries(
          ' ',
          citiesDataSet.filter('size', filterFunction(200000, 300000)),
          '#26c6da'
        );
        createSeries(
          ' ',
          citiesDataSet.filter('size', filterFunction(300000, 400000)),
          '#00acc1'
        );
        createSeries(
          ' ',
          citiesDataSet.filter('size', filterFunction(400000, 500000)),
          '#0097a7'
        );
        createSeries(
          ' ',
          citiesDataSet.filter('size', filterFunction(500000, 1000000)),
          '#00838f'
        );
        createSeries(
          ' ',
          citiesDataSet.filter('size', filterFunction(1000000)),
          '#006064'
        );

        // turns on the legend for the sample
        // map.legend().enabled(true);

        // create zoom controls
        var zoomController = anychart.ui.zoom();
        zoomController.render(map);

        // sets container id for the chart
        map.container('container');
        // initiates chart drawing
        map.draw();
      }
    );
  });

  // helper function to bind data field to the local var.
  function filterFunction(val1, val2) {
    if (val2) {
      return function (fieldVal) {
        return val1 <= fieldVal && fieldVal < val2;
      };
    }
    return function (fieldVal) {
      return val1 <= fieldVal;
    };
  }
