import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard";
import ChatInterface from "./components/ChatInterface";
import ProjectView from "./components/ProjectView";

function App() {
  return (
    <div className="App dark">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/chat" element={<ChatInterface />} />
          <Route path="/project/:id" element={<ProjectView />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;