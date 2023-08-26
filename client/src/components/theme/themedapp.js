import React from 'react'
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import ThemedAppBar from './themedappbar';
// import ImgMediaCard from './ImgMediaCard'

// See default palette at https://mui.com/material-ui/customization/palette/
const theme = createTheme({
  palette: {
    mode: 'light',
  },
  typography: {
    fontFamily: [
      "Times New Roman"
    ]
  }
});

const style = { 
  height: "100vh",
  width: "100vw",
  display: "flex",
  flexDirection: "column",
  backgroundColor: "green"
}

export default function ThemedApp({children}) {
  return (
    <ThemeProvider theme={theme}>
      <div style={style}>
        <div>
          <ThemedAppBar />
          <CssBaseline />
        </div>
        <div style={{flex: 1, display: "flex", flexDirection: "column"}}>
          {children}
        </div>
      </div>
    </ThemeProvider>
  )
}
