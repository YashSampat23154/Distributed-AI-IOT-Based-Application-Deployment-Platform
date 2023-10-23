import React, { useEffect, useRef, useState } from 'react'
import Cards from '../Cards/Cards';
import './MainDash.css'
// import ReactMapGL, { Map, Layer, Feature, Marker, Popup } from 'react-mapbox-gl';
// import mapboxgl from 'mapbox-gl';
// import 'mapbox-gl/dist/mapbox-gl.css';
// import L from 'leaflet';
import 'ol/ol.css';
import { Map, View } from 'ol';
import { fromLonLat } from 'ol/proj';
import { Tile as TileLayer, Vector as VectorLayer } from 'ol/layer';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector';
import { Circle as CircleStyle, Fill, Stroke, Style } from 'ol/style';
import Feature from 'ol/Feature';
import Point from 'ol/geom/Point';
import Overlay from 'ol/Overlay';
// const Mapbox = ReactMapboxGl({
//     accessToken: 'pk.eyJ1Ijoic2lkZGg1NTk5IiwiYSI6ImNsZ2J3a3JpbTFmMGgzeHBpaGtzNTgwMG8ifQ.1C1ptF8VDzXqZTle59_3PA',
//     attributionControl: false,
//     logoPosition: 'bottom-right'
// });

const MainDash = () => {
  const [map, setMap] = useState(null);
  const mapElement = useRef(null);
  const [points, setPoints] = useState([
    [78.23, 17.455],
    [78.013, 17.559],
    [78.486, 17.385]
  ]);

  useEffect(() => {
    // Initialize the map with a view centered on San Francisco
    const initialMap = new Map({
      target: mapElement.current,
      layers: [
        new TileLayer({
          source: new OSM(),
        }),
      ],
      view: new View({
        center: fromLonLat([78.486, 17.385]),
        zoom: 13,
      }),
    });

    setMap(initialMap);
  }, []);

  useEffect(() => {
    // Add points for the coordinates in the points array
    if (map) {
      const pointsLayer = new VectorLayer({
        source: new VectorSource({
          features: points.map((point) => {
            return new Feature({
              geometry: new Point(fromLonLat(point)),
            });
          }),
        }),
        style: new Style({
          image: new CircleStyle({
            radius: 6,
            fill: new Fill({ color: 'blue' }),
            stroke: new Stroke({ color: 'white', width: 2 }),
          }),
        }),
      });

      map.addLayer(pointsLayer);

      // Add a popup when clicking on a point
      const popupElement = document.createElement('div');
      popupElement.className = 'ol-popup';

      const popup = new Overlay({
        element: popupElement,
        positioning: 'bottom-center',
        stopEvent: false,
        offset: [0, -20],
      });
      map.addOverlay(popup);

      map.on('click', (event) => {
        const feature = map.forEachFeatureAtPixel(event.pixel, (feature) => feature);
        if (feature) {
          const coordinates = feature.getGeometry().getCoordinates();
          popup.setPosition(coordinates);
          popupElement.innerHTML = '<p>You clicked on a point!</p>';
        } else {
          popup.setPosition(undefined);
        }
      });

      // Center the map on the points
      const pointsExtent = pointsLayer.getSource().getExtent();
      map.getView().fit(pointsExtent);
    }
  }, [map, points]);

  return (
    <div className='MainDash'>
      <h1>Dashboard</h1>
      <Cards />
      <h4>Registered Sensor Locations</h4>
      <div ref={mapElement} style={{ width: '100%', height: '500px' }} />
    </div>
  );

};

export default MainDash;