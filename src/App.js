import ThemedApp from './components/theme/themedapp';
import './App.css';
import Board from './components/board';
import Interaction from './components/interaction';
import { APP_BAR_HEIGHT } from './components/theme/themedappbar';

const PADDING = "10px"
const LEFT_COL = "250px"
const RIGHT_COL = "250px"
const CENTER_WIDTH = `calc(100vw - ${PADDING} - ${PADDING} - ${RIGHT_COL} - ${LEFT_COL})`
const CENTER_HEIGHT = `calc(100vh - ${PADDING} - ${PADDING} - ${APP_BAR_HEIGHT})`
const INTERACTION_HEIGHT = "250px"

function App() {
  return (
    <ThemedApp>
      <div style={{flex: 1, display: "flex", flexDirection: "row", backgroundColor: "yellow", padding: PADDING}}>
        <div style={{minWidth: LEFT_COL, display: "flex", flexDirection: "column"}}>
          <div style={{height: INTERACTION_HEIGHT, backgroundColor: "pink"}}>
            <Interaction/>
          </div>
          <div style={{height: PADDING}}></div>
          <div style={{flex: 1, backgroundColor: "pink"}}>Messages</div>
        </div>
        <div style={{width: PADDING}}></div>
        <div style={{flex: 1, width: CENTER_WIDTH, height: CENTER_HEIGHT, display: "flex", backgroundColor: "pink", overflow: "auto"}}>
          <Board/>
        </div>
        <div style={{width: PADDING}}></div>
        <div style={{minWidth: RIGHT_COL, backgroundColor: "pink"}}>Scores</div>
      </div>
    </ThemedApp>
  );
}

export default App;
