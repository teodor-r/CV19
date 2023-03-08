var myMap;

var xhr = new XMLHttpRequest();
xhr.open('GET', 'http://109.196.164.48/map.php', false);
xhr.send();

let  databases;
// 4. Если код ответа сервера не 200, то это ошибка
if (xhr.status != 200) {
  // обработать ошибку
  alert( xhr.status + ': ' + xhr.statusText ); // пример вывода: 404: Not Found
} else {
  // вывести результат
  //alert( xhr.responseText ); // responseText -- текст ответа.

}
databases = JSON.parse(xhr.responseText);

ymaps.ready(init);

function init () {
    // Создание экземпляра карты и его привязка к контейнеру с
    // заданным id ("map").
    myMap = new ymaps.Map('map', {
        // При инициализации карты обязательно нужно указать
        // её центр и коэффициент масштабирования.
        center: [51.828508, 107.585347], // Москва
        zoom: 10
    }, {
        searchControlProvider: 'yandex#search'
    }),
    clusterer2 = new ymaps.Clusterer({
            /**
             * Через кластеризатор можно указать только стили кластеров,
             * стили для меток нужно назначать каждой метке отдельно.
             * @see https://api.yandex.ru/maps/doc/jsapi/2.1/ref/reference/option.presetStorage.xml
             */
            preset: 'islands#redClusterIcons',

            /**
             * Ставим true, если хотим кластеризовать только точки с одинаковыми координатами.
             */
            groupByCoordinates: false,
            /**
             * Опции кластеров указываем в кластеризаторе с префиксом "cluster".
             * @see https://api.yandex.ru/maps/doc/jsapi/2.1/ref/reference/ClusterPlacemark.xml
             */
            clusterDisableClickZoom: true,
            clusterHideIconOnBalloonOpen: false,
            geoObjectHideIconOnBalloonOpen: false
        }),
    clusterer1 = new ymaps.Clusterer({
            /**
             * Через кластеризатор можно указать только стили кластеров,
             * стили для меток нужно назначать каждой метке отдельно.
             * @see https://api.yandex.ru/maps/doc/jsapi/2.1/ref/reference/option.presetStorage.xml
             */
            preset: 'islands#ClusterIcons',
            /**
             * Ставим true, если хотим кластеризовать только точки с одинаковыми координатами.
             */
            groupByCoordinates: false,
            /**
             * Опции кластеров указываем в кластеризаторе с префиксом "cluster".
             * @see https://api.yandex.ru/maps/doc/jsapi/2.1/ref/reference/ClusterPlacemark.xml
             */
            clusterDisableClickZoom: true,
            clusterHideIconOnBalloonOpen: false,
            geoObjectHideIconOnBalloonOpen: false
        });

    for (let key in databases.base1) {

     let coords = [databases.base1[key].y,databases.base1[key].x];
        var placemark = new ymaps.Placemark(coords, {
            hintContent: databases.base1[key].district,
            balloonContent: databases.base1[key].district + ". Cлучаев: " + String(databases.base1[key].amount),
            iconContent: String(databases.base1[key].amount),
            clusterCaption: databases.base1[key].district
            }, {
            // Опции.
            preset:   'islands#'
            });
        clusterer1.add(placemark);
    }

    for (let key in databases.base2) {

     let coords = [databases.base2[key].y ,databases.base2[key].x];
        var placemark = new ymaps.Placemark(coords, {
            hintContent: databases.base2[key].date,
            balloonContent: "Дата:" + databases.base2[key].date + ", cлучай:"+ String(databases.base2[key].num),
            iconContent: String(databases.base2[key].case),
            clusterCaption: "Дата:" + databases.base2[key].date + ", cлучай:"+ String(databases.base2[key].num)
            }, {
            // Опции.
            preset:   'islands#redDotIcon'
            });
        clusterer2.add(placemark);
    }
    

	myMap.geoObjects.add(clusterer1);
	myMap.geoObjects.add(clusterer2);

	 myMap.setBounds(clusterer.getBounds(), {
        checkZoomRange: true
    });

}