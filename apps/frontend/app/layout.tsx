import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MEMORIA AI',
  description: 'Your Personal AI Operating System',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
