import { BrowserRouter, Routes, Route, useNavigate } from "react-router-dom";
import AppBar, { type MenuOption, type ProfileOption } from "./components/AppBar";
import Home from "./pages/Home";
import TrackEditor from "./pages/TrackEditor";
import TrackLayout from "./pages/TrackLayout";
import { useWebSocket } from "./hooks/useWebsocket";
import "./App.css"

function AppContent() {
  const navigate = useNavigate();
  const { sendMessage } = useWebSocket("wss://react.brandonfremin.com/api/ws/heartbeat");
  sendMessage("Hello from the client!");

  const menuOptions: MenuOption[] = [
    { label: "Home", onClick: () => navigate("/") },
    { label: "Tracks", onClick: () => navigate("/tracks") },
    { label: "Layout", onClick: () => navigate("/layout") }
  ];

  const profileOptions: ProfileOption[] = [
    { label: "Profile", onClick: () => console.log("Profile clicked") },
    { label: "Settings", onClick: () => console.log("Settings clicked") },
    { label: "Logout", onClick: () => console.log("Logout clicked") }
  ];

  const routes = [
    { to: "/", label: "Home", component: Home },
    { to: "/tracks", label: "Tracks", component: TrackEditor },
    { to: "/layout", label: "Layout", component: TrackLayout }
  ];

  return (
    <div className="min-h-screen w-full bg-white flex flex-col">
      <AppBar 
        title="Tom's Train Room"
        menuOptions={menuOptions}
        profileOptions={profileOptions}
      />

      <div className="flex-1 p-4">
        <Routes>
          {routes.map((route) => <Route key={route.to} path={route.to} element={<route.component />} />)}
        </Routes>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}

export default App
