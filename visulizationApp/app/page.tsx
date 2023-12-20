'use client'
import * as React from 'react';
import { useRef, useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import { Map, Source, Layer } from 'react-map-gl';
import FeatureDrawer from './components/FeatureDrawer'

// import ControlPanel from './control-panel';
import {clusterLayer, clusterCountLayer, unclusteredPointLayer} from './components/layers';

import type {MapRef} from 'react-map-gl';
import type {GeoJSONSource} from 'react-map-gl';

const MAPBOX_TOKEN = process.env.NEXT_PUBLIC_MAPBOX_TOKEN; // Set your mapbox token here

export default function App() {
  const mapRef = useRef<MapRef>(null);
  // const [drawerOpen, setDrawerOpen] = useState(false);
  const [data, setData] = useState(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
const [selectedFeatures, setSelectedFeatures] = useState([]);
const [nodeType, setNodeType] = useState('single'); // 'cluster' 或 'single'

  useEffect(() => {
    // 异步加载 GeoJSON 数据
    const fetchData = async () => {
      const response = await fetch('/images2/outputGeoJSON.json');
      const jsonData = await response.json();
      setData(jsonData);
    };

    fetchData();
  }, []);

  const onClick = event => {
    const map = mapRef.current.getMap();
    const features = mapRef?.current.queryRenderedFeatures(event.point, {
      layers: ['unclustered-point', 'clusters']
    });
  
    if (!features.length) {
      return;
    }
  
    const feature = features[0];
    
  
    // 判断点击的是否是聚合点
    if (feature.properties.cluster) {

      const clusterId = feature.properties.cluster_id;
      const clusterSource = map.getSource('postcards'); // 确保源名称与你的相符
      setNodeType('cluster');
      clusterSource.getClusterLeaves(clusterId, 50, 0, (error, leaves) => {
        setSelectedFeatures(leaves);
      });
    } else {
      setNodeType('single');
      setSelectedFeatures([feature]);
    }

    // const feature = features[0];
    // setSelectedFeature(feature);
    setDrawerOpen(true);
  };

  return (
    <>
      <Map
        initialViewState={{
          latitude: 46.5196,  // 洛桑的纬度
          longitude: 6.6323,  // 洛桑的经度
          zoom: 5            // 调整为合适的缩放级别
        }}
        mapStyle="mapbox://styles/mapbox/light-v10"
        mapboxAccessToken={MAPBOX_TOKEN}
        interactiveLayerIds={[clusterLayer.id]}
        onClick={onClick}
        ref={mapRef}
        style={{ width: '100vw', height: '100vh' }}
        // onLoad={onMapLoad}
      >
        <Source
          id="postcards"
          type="geojson"
          data="/images2/outputGeoJSON.json" // 指向您的 GeoJSON 文件
          cluster={true}
          clusterMaxZoom={14} // 在此缩放级别以上不再聚合
          clusterRadius={50} // 聚合半径（像素）
        >
          <Layer {...clusterLayer} />
          <Layer {...clusterCountLayer} />
          <Layer {...unclusteredPointLayer} />
        </Source>

      </Map>
      <FeatureDrawer
      open={drawerOpen}
      onClose={() => setDrawerOpen(false)}
      features={selectedFeatures}
      type={nodeType}
    />
      {/* <ControlPanel /> */}
    </>
  );
}

export function renderToDom(container) {
  createRoot(container).render(<App />);
}