import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Shield } from 'lucide-react';
import { CITTAA_COLORS } from '@/lib/utils';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div 
      className="min-h-screen flex items-center justify-center p-4"
      style={{ backgroundColor: CITTAA_COLORS.lightBg }}
    >
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div 
            className="inline-flex items-center justify-center w-16 h-16 rounded-full mb-4"
            style={{ backgroundColor: CITTAA_COLORS.purple }}
          >
            <Shield className="w-8 h-8 text-white" />
          </div>
          <h1 
            className="text-3xl font-bold"
            style={{ color: CITTAA_COLORS.purple }}
          >
            CITTAA
          </h1>
          <p 
            className="text-sm mt-1"
            style={{ color: CITTAA_COLORS.warmGray }}
          >
            Internal Escalation AI Engine
          </p>
        </div>

        <Card className="shadow-lg border-0">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl text-center">Sign In</CardTitle>
            <CardDescription className="text-center">
              Enter your credentials to access the escalation portal
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              <div className="space-y-2">
                <label 
                  htmlFor="email" 
                  className="text-sm font-medium"
                  style={{ color: CITTAA_COLORS.darkText }}
                >
                  Email
                </label>
                <Input
                  id="email"
                  type="email"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  className="h-11"
                />
              </div>

              <div className="space-y-2">
                <label 
                  htmlFor="password" 
                  className="text-sm font-medium"
                  style={{ color: CITTAA_COLORS.darkText }}
                >
                  Password
                </label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  className="h-11"
                />
              </div>

              <Button
                type="submit"
                className="w-full h-11 text-white transition-all duration-200 hover:opacity-90"
                style={{ backgroundColor: CITTAA_COLORS.purple }}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  'Sign In'
                )}
              </Button>
            </form>

            <div className="mt-6 pt-6 border-t text-center">
              <p 
                className="text-xs"
                style={{ color: CITTAA_COLORS.warmGray }}
              >
                CITTAA Health Services Private Limited
              </p>
              <p 
                className="text-xs mt-1"
                style={{ color: CITTAA_COLORS.warmGray }}
              >
                Bridging Mental Health Gaps Through Intelligent Wellness Solutions
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
