import React, {useState, useEffect} from 'react';
import Box  from '@material-ui/core/Box';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import { GridList } from '@material-ui/core';
import axios from 'axios';


import StatePLCCard from './stateplccard';
import branch from '../../assets/branch.png';
import storage from '../../assets/storage.png';
import robotino from '../../assets/robotino.png';


export default function ListStates(){

    const IP_BACKEND = "127.0.0.1";
    //let IP_BACKEND ="129.69.102.129";

    // React hooks
    const [state, setState] =useState([])
    useEffect(() => {
        getDataFromMes()
    }, [])

    function createListItem(statesPLC){
        let items = []
        statesPLC.sort((a, b) => (a.id> b.id) ? 1 : -1)
        for( let i=0; i<statesPLC.length; i++){
                // get image depending on resourceId
                let img = null;
                if (statesPLC[i].id ===1){
                    img= storage;
                } else if(statesPLC[i].id <7){
                    img= branch;
                } else {
                    img= robotino;
                }
            
                items.push(
                <ListItem  width = "100%">
                    <StatePLCCard 
                    name= {statesPLC[i].name} 
                    mode={statesPLC[i].mode} 
                    image= {img} 
                    state={statesPLC[i].state} 
                    resourceId= {statesPLC[i].id} 
                    />
                </ListItem>
                );
            }
        return items;
        
    }

    function getDataFromMes(){
            axios.get("http://" + IP_BACKEND + ":8000/api/StatePLC/")
                .then( res =>{
                        setState(res.data)
                    });
        }

    return(
                <GridList cellHeight={170} cols={3} spacing={20}>
                  {createListItem(state)}
                </GridList>

    );
};