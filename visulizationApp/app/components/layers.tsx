export const clusterLayer: LayerProps = {
  id: 'clusters',
  type: 'circle',
  source: 'postcards',
  filter: ['has', 'point_count'],
  paint: {
    'circle-color': ['step', ['get', 'point_count'], '#51bbd6', 100, '#f1f075', 750, '#f28cb1'],
    'circle-radius': [
        'step',
        ['get', 'point_count'],
        20,  // 少于100个点时的大小
        100,
        40,  // 100到750个点时的大小
        750,
        60  // 超过750个点时的大小
      ]  
  },
};

export const clusterCountLayer: LayerProps = {
  id: 'cluster-count',
  type: 'symbol',
  source: 'postcards',
  filter: ['has', 'point_count'],
  layout: {
    'text-field': '{point_count_abbreviated}',
    'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
    'text-size': 14,
    'text-color': '#ffffff',
    'text-halo-color': '#000000',
    'text-halo-width': 1
  }
};

export const unclusteredPointLayer: LayerProps = {
  id: 'unclustered-point',
  type: 'circle',
  source: 'postcards',
  filter: ['!', ['has', 'point_count']],
  paint: {
    'circle-color': '#11b4da',
    'circle-radius': 10,
    'circle-stroke-width': 2,
    'circle-stroke-color': '#fff'
  }
};
