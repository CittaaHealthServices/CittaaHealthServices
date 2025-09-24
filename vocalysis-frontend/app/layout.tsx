import './globals.css';
import { ReactNode } from 'react';

export const metadata = {
  title: 'CITTAA Vocalysis Demo',
  description: 'AI-Powered Mental Health Screening for India'
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="icon" href="/logo.svg" />
      </head>
      <body>{children}</body>
    </html>
  );
}
