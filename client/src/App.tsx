import './App.css'
import Chat from './components/Chat'

function App() {
  return (
    <Chat 
      apiUrl="http://localhost:8000" 
      systemPrompt="default" 
    />
  )
}

export default App
