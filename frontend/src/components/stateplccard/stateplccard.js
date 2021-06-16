import React from 'react';
import Box  from '@material-ui/core/Box';
import Card from '@material-ui/core/Card';
import CardActionArea from '@material-ui/core/CardActionArea';
import CardActions from '@material-ui/core/CardActions';
import CardContent from '@material-ui/core/CardContent';
import CardMedia from '@material-ui/core/CardMedia';
import Button from '@material-ui/core/Button';
import Typography from '@material-ui/core/Typography';


export default function StatePLCCard(props){
    
    let name = "";
    let mode ="";
    let state = "";
    let image ="";
    let resourceId = "";

    if(props.name){
        name =props.name;
    } if(props.image){
        image= props.image;
    } if(props.state){
        state= props.state;
    } if(props.mode){
        mode= props.mode;
    } if(props.resourceId){
        resourceId= props.resourceId;
    } 
  
  return (
    <Card >
      <CardActionArea>
        <CardMedia
          component="img"
          alt="Image of resource"
          image={image}
          height="100%"
          title="Image of resource"
        />
        <CardContent>
          <Typography gutterBottom variant="h5" component="h2">
            {name}
          </Typography>
          <Typography variant="body1" color="textSecondary" component='div'>
            <Box fontWeight='fontWeightBold' display='inline'>State :</Box> {state}
          </Typography>
          <Typography variant="body1" color="textSecondary" component='div'>
            <Box fontWeight='fontWeightBold' display='inline'>ResourceId :</Box> {resourceId}
          </Typography>
          <Typography variant="body1" color="textSecondary" component='div'>
            <Box fontWeight='fontWeightBold' display='inline'>Mode :</Box> {mode}
          </Typography>
        </CardContent>
      </CardActionArea>
      <CardActions>
        <Button size="small" color="primary">
          Edit
        </Button>
      </CardActions>
    </Card>
  );


}