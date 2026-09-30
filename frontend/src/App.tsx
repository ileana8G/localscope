import { Route, Routes } from "react-router-dom";
import HomePage from "./pages/Home/HomePage";
import LocalityPage from "./pages/Locality/LocalityPage";
import CountyPage from "./pages/County/CountyPage";

function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/locality/:siruta" element={<LocalityPage />} />
      <Route path="/county/:nuts3" element={<CountyPage />} />
    </Routes>
  );
}

export default App;
