import { useEffect, useState } from "react";
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import LinearProgress from '@mui/material/LinearProgress';
import Box from '@mui/material/Box';
import CheckCircle from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';

import httpImg from "../assets/http.png";
import wsImg from "../assets/ws.png";
import cassandraImg from "../assets/cassandra.png";
import trainImg from "../assets/train.png";
import lionelImg from "../assets/lionel.webp";
import grafanaImg from "../assets/grafana.png";
import lokiImg from "../assets/loki.png";

import { selectPingHttp, selectPingWs, selectPingCassandra, selectPingLoki, selectPingGrafana, selectPingTrain, selectPingLionel } from "../redux/pingSelector";
import { useAppSelector } from "../redux/store";

type CardProps = {
  img: string;   // path or URL to an image
  status: string;   // a text label
};

function MediaCard(props: CardProps) {
  const size = 150
  const circleStyle = props.status === "WAIT" ? {} : {
    display: 'flex',
    justifyContent: 'center'
  }
  return (
    <Card sx={{ width: size }}>
      <CardMedia
        sx={{ height: size, width: size }}
        image={props.img}
      />
      <CardContent>
        <Box sx={{ width: '100%', ...circleStyle }}>
          {
            props.status === "WAIT" ?
              <LinearProgress /> : props.status === "FAIL" ?
                <CancelIcon color="error" /> :
                <CheckCircle color="success" />
          }
        </Box>
      </CardContent>
    </Card>
  );
}

export default function Home() {
  const http = useAppSelector(selectPingHttp);
  const ws = useAppSelector(selectPingWs);
  const cassandra = useAppSelector(selectPingCassandra);
  const loki = useAppSelector(selectPingLoki);
  const grafana = useAppSelector(selectPingGrafana);
  const train = useAppSelector(selectPingTrain);
  const lionel = useAppSelector(selectPingLionel);

  return (
    <div>
      <div className="flex flex-row flex-wrap gap-10 justify-center">
        <MediaCard img={httpImg} status={http} />
        <MediaCard img={wsImg} status={ws} />
        <MediaCard img={cassandraImg} status={cassandra} />
        <MediaCard img={lokiImg} status={loki} />
        <MediaCard img={grafanaImg} status={grafana} />
        <MediaCard img={trainImg} status={train} />
        <MediaCard img={lionelImg} status={lionel} />
      </div>
    </div>
  )
}