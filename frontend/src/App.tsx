import { Route, Routes } from "react-router-dom";
import HomePage from "./pages/Home/HomePage";
import LocalityPage from "./pages/Locality/LocalityPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/locality/:siruta" element={<LocalityPage />} />
    </Routes>
  );
}

export default App;
