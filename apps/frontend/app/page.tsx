export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">MEMORIA AI</h1>
        <p className="text-xl mb-8">Your Personal AI Operating System</p>
        <div className="grid gap-4">
          <div className="p-4 border rounded-lg">
            <h2 className="font-bold mb-2">Backend API</h2>
            <p className="text-sm">http://localhost:8000</p>
            <p className="text-sm">API Docs: http://localhost:8000/docs</p>
          </div>
          <div className="p-4 border rounded-lg">
            <h2 className="font-bold mb-2">Status</h2>
            <p className="text-sm">Initializing project structure...</p>
          </div>
        </div>
      </div>
    </main>
  )
}
