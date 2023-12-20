'use client'

import React, { useState } from 'react';
import ReactMapGL, { Marker } from 'react-map-gl';
import postData from '../public/images/output.json';

function MapComponent() {
  const [viewport, setViewport] = useState({
    width: '100vw',
    height: '100vh',
    latitude: 0,    // 初始纬度
    longitude: 0,   // 初始经度
    zoom: 2         // 初始缩放级别
  });

  return (
    <ReactMapGL
      {...viewport}
      onViewportChange={(nextViewport) => setViewport(nextViewport)}
      mapboxApiAccessToken={process.env.NEXT_PUBLIC_MAPBOX_TOKEN}>
      {postData.map((postcard, index) => (
        <Marker
          latitude={parseFloat(postcard.coordinates.latitude)}
          longitude={parseFloat(postcard.coordinates.longitude)}
          key={index}>
          {/* 在这里渲染每个 postcard 的缩略图和数量 */}
        </Marker>
      ))}
    </ReactMapGL>
  );
}

export default MapComponent;
