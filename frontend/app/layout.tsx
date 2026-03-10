import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI Contract Risk Detector',
  description: 'Multi-agent AI system for contract risk analysis before signing',
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
