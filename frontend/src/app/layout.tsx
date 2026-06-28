import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SAHAYAK-AI - Disaster Response',
  description: 'State-Aware Hazard Assistance & Yielding Action Knowledge',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        {children}
      </body>
    </html>
  )
}
