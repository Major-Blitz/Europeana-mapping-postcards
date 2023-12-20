import React, { useState } from 'react';
import Drawer from '@mui/material/Drawer';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Skeleton from '@mui/material/Skeleton';
import Image from 'next/image';
import Dialog from '@mui/material/Dialog';
import Card from '@mui/material/Card';
import CardMedia from '@mui/material/CardMedia';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';

const defaultImageUrl = '/path/to/default/image.jpg'; 

const FeatureDrawer = ({ open, onClose, features, type }) => {
  const [imageLoadStatus, setImageLoadStatus] = useState(features.map(() => 'loading'));
  const [selectedImage, setSelectedImage] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);

  const handleImageLoad = (index) => {
    setImageLoadStatus(status => ({ ...status, [index]: 'loaded' }));
  };

  const handleImageError = (index) => {
    setImageLoadStatus(status => ({ ...status, [index]: 'error' }));
    features[index].properties.url = defaultImageUrl;
  };

  const handleImageClick = (url, event) => {
    event.stopPropagation();
    setSelectedImage(url);
    setIsDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setSelectedImage(null);
  };

  return (
    <Drawer anchor="left" open={open} onClose={onClose}>
      <Box sx={{ width: 800, p: 2 }} role="presentation" onClick={onClose} onKeyDown={onClose}>
        <Grid container spacing={2}>
          {features.map((feature, index) => (
            <Grid item xs={12} sm={6} md={4} key={index}>
            <Card sx={{ height: 280 }}>
              <CardMedia
                component="img"
                sx={{ height:200}}
                image={imageLoadStatus[index] === 'error' ? defaultImageUrl : `/images/${feature.properties.url}`}
                alt={`Postcard ${index}`}
              />
              <CardContent sx={{ height: 160 }}> {/* 确保足够的空间给文字内容 */}
                <Typography variant="h6" component="div" noWrap>
                  {feature.properties.city || 'Unknown City'}
                </Typography>
                <Typography variant="body2" color="text.secondary" noWrap>
                  {feature.properties.country || 'Unknown Country'}
                </Typography>
              </CardContent>
            </Card>

            </Grid>
          ))}
        </Grid>
      </Box>

      <Dialog open={isDialogOpen} onClose={handleCloseDialog}>
        <img src={selectedImage} alt="Selected" style={{ width: '100%', height: 'auto' }} />
      </Dialog>
    </Drawer>
  );
};

export default FeatureDrawer;
