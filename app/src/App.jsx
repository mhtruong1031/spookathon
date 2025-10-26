import { useState } from 'react'
import Landing from './Pages/Landing.jsx'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <title>ARithmetic</title>
      <Landing />
    </>
  )
}

export default App
