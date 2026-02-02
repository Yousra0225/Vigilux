import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-background text-foreground">
      <div className="z-10 max-w-5xl w-full flex flex-col items-center gap-8 text-center">
        <h1 className="text-6xl font-extrabold tracking-tight">Vigilux</h1>
        <p className="text-xl text-muted-foreground max-w-[600px]">
          Transformez la veille concurrentielle passive en signaux d'action proactifs grâce à l'IA.
        </p>
        
        <div className="flex gap-4">
          <Link 
            href="/login" 
            className="px-8 py-3 rounded-md bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            Se connecter
          </Link>
          <Link 
            href="/register" 
            className="px-8 py-3 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground font-medium transition-colors"
          >
            Créer un compte
          </Link>
        </div>
      </div>
    </main>
  );
}
