/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ["class"],
    content: ["./index.html", "./src/**/*.{ts,tsx,js,jsx}"],
  theme: {
  	extend: {
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
  		colors: {
  			// CITTAA Brand Colors (Brand Kit v1.0)
  			cittaa: {
  				purple: '#8B5A96',
  				'purple-light': '#B085BA',
  				'purple-dark': '#5D3D66',
  				teal: '#7BB3A8',
  				'teal-light': '#A8D4CB',
  				'teal-dark': '#4E8A7D',
  				blue: '#1E3A8A',
  				'blue-light': '#3B5998',
  			},
  			// Semantic Colors (Mental Health States)
  			'healing-green': '#10B981',
  			'warning-yellow': '#F59E0B',
  			'alert-orange': '#F97316',
  			'danger-red': '#DC2626',
  			// Clinical Scale Colors
  			'phq9': '#DC2626',
  			'gad7': '#F59E0B',
  			'pss': '#F97316',
  			'wemwbs': '#10B981',
  			sidebar: {
  				DEFAULT: 'hsl(var(--sidebar-background))',
  				foreground: 'hsl(var(--sidebar-foreground))',
  				primary: 'hsl(var(--sidebar-primary))',
  				'primary-foreground': 'hsl(var(--sidebar-primary-foreground))',
  				accent: 'hsl(var(--sidebar-accent))',
  				'accent-foreground': 'hsl(var(--sidebar-accent-foreground))',
  				border: 'hsl(var(--sidebar-border))',
  				ring: 'hsl(var(--sidebar-ring))'
  			}
  		},
  		keyframes: {
  			'accordion-down': {
  				from: {
  					height: '0'
  				},
  				to: {
  					height: 'var(--radix-accordion-content-height)'
  				}
  			},
  			'accordion-up': {
  				from: {
  					height: 'var(--radix-accordion-content-height)'
  				},
  				to: {
  					height: '0'
  				}
  			}
  		},
  		animation: {
  			'accordion-down': 'accordion-down 0.2s ease-out',
  			'accordion-up': 'accordion-up 0.2s ease-out'
  		}
  	}
  },
  plugins: [import("tailwindcss-animate")],
}

