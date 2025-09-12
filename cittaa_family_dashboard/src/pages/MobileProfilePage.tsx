import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Smartphone, Download, Shield, CheckCircle, Copy, ExternalLink } from 'lucide-react';
import { familyApi } from '@/lib/api';
import { useFamily } from '@/contexts/FamilyContext';
import { useAuth } from '@/contexts/AuthContext';

interface MobileProfile {
  id: number;
  child_name: string;
  device_type: string;
  downloaded: boolean;
  activated: boolean;
  created_at: string;
  download_token?: string;
}

export default function MobileProfilePage() {
  const { children } = useFamily();
  const { token } = useAuth();
  const [profiles, setProfiles] = useState<MobileProfile[]>([]);
  const [loading, setLoading] = useState(false);
  const [generatedProfile, setGeneratedProfile] = useState<any>(null);

  useEffect(() => {
    loadProfiles();
  }, []);

  const generateProfile = async (childId: number, deviceType: string) => {
    if (!token) return;
    
    setLoading(true);
    try {
      const response = await familyApi.generateMobileProfile(token, {
        child_id: childId,
        device_type: deviceType,
        device_id: `${deviceType}_${Date.now()}`
      });
      
      setGeneratedProfile({
        ...(response as any),
        device_type: deviceType,
        child_id: childId
      });
      
      loadProfiles();
    } catch (error) {
      console.error('Failed to generate profile:', error);
      alert('Failed to generate mobile profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadProfiles = async () => {
    if (!token) return;
    
    try {
      const response = await familyApi.listMobileProfiles(token);
      setProfiles((response as any).profiles || []);
    } catch (error) {
      console.error('Failed to load profiles:', error);
    }
  };

  const copyDownloadUrl = (token: string) => {
    const baseUrl = 'https://app-elkjjhso.fly.dev';
    const downloadUrl = `${baseUrl}/mobile-profile/download/${token}`;
    navigator.clipboard.writeText(downloadUrl);
    alert('Download URL copied to clipboard!');
  };

  const openDownloadUrl = (token: string) => {
    const baseUrl = 'https://app-elkjjhso.fly.dev';
    const downloadUrl = `${baseUrl}/mobile-profile/download/${token}`;
    window.open(downloadUrl, '_blank');
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-[#8B5A96]">Mobile Profiles</h1>
        <p className="text-gray-600 mt-2">
          Generate and manage mobile safety profiles for your children's devices
        </p>
      </div>

      {generatedProfile && (
        <Card className="border-green-200 bg-green-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-800">
              <CheckCircle className="h-5 w-5" />
              Profile Generated Successfully!
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="bg-white p-4 rounded-lg border">
              <h4 className="font-semibold mb-2">Download Instructions:</h4>
              <ol className="list-decimal list-inside space-y-2 text-sm">
                <li>Copy the download URL below</li>
                <li>Share it with your child or help them access it on their {generatedProfile.device_type} device</li>
                <li>The profile will automatically configure safety settings</li>
                <li>Your child will see transparent explanations of all protection features</li>
              </ol>
            </div>
            <div className="flex gap-2">
              <Button
                onClick={() => copyDownloadUrl(generatedProfile.download_token)}
                className="bg-[#8B5A96] hover:bg-[#8B5A96]/90"
              >
                <Copy className="h-4 w-4 mr-2" />
                Copy Download URL
              </Button>
              <Button
                onClick={() => openDownloadUrl(generatedProfile.download_token)}
                variant="outline"
                className="border-[#7BB3A8] text-[#7BB3A8] hover:bg-[#7BB3A8]/10"
              >
                <ExternalLink className="h-4 w-4 mr-2" />
                Open Profile
              </Button>
            </div>
            <Button
              onClick={() => setGeneratedProfile(null)}
              variant="ghost"
              size="sm"
            >
              Dismiss
            </Button>
          </CardContent>
        </Card>
      )}

      {children?.map((child: any) => (
        <Card key={child.id} className="border-[#7BB3A8]/20">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Smartphone className="h-5 w-5 text-[#8B5A96]" />
              {child.name}'s Mobile Profiles
            </CardTitle>
            <CardDescription>
              Generate safety profiles for {child.name}'s devices
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <Button
                onClick={() => generateProfile(child.id, 'ios')}
                disabled={loading}
                className="bg-[#8B5A96] hover:bg-[#8B5A96]/90"
              >
                <Download className="h-4 w-4 mr-2" />
                Generate iOS Profile
              </Button>
              <Button
                onClick={() => generateProfile(child.id, 'android')}
                disabled={loading}
                variant="outline"
                className="border-[#7BB3A8] text-[#7BB3A8] hover:bg-[#7BB3A8]/10"
              >
                <Download className="h-4 w-4 mr-2" />
                Generate Android Profile
              </Button>
            </div>
            
            <div className="bg-[#7BB3A8]/10 p-4 rounded-lg">
              <h4 className="font-semibold text-[#8B5A96] mb-2">Profile Features:</h4>
              <ul className="text-sm space-y-1">
                <li>✅ Transparent content filtering with educational explanations</li>
                <li>✅ Age-appropriate consent mechanisms</li>
                <li>✅ VPN detection and blocking</li>
                <li>✅ Educational content promotion</li>
                <li>✅ DPDP Act 2023 compliance</li>
              </ul>
            </div>

            {profiles.filter(p => p.child_name === child.name).length > 0 && (
              <div className="space-y-2">
                <h4 className="font-semibold text-[#8B5A96]">Existing Profiles:</h4>
                {profiles
                  .filter(p => p.child_name === child.name)
                  .map((profile) => (
                    <div key={profile.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                      <div className="flex items-center gap-3">
                        <Smartphone className="h-4 w-4 text-gray-500" />
                        <span className="font-medium">{profile.device_type.toUpperCase()}</span>
                        <Badge variant={profile.activated ? "default" : profile.downloaded ? "secondary" : "outline"}>
                          {profile.activated ? "Active" : profile.downloaded ? "Downloaded" : "Pending"}
                        </Badge>
                      </div>
                      {profile.download_token && !profile.downloaded && (
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => copyDownloadUrl(profile.download_token!)}
                          >
                            <Copy className="h-3 w-3 mr-1" />
                            Copy URL
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openDownloadUrl(profile.download_token!)}
                          >
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Open
                          </Button>
                        </div>
                      )}
                    </div>
                  ))}
              </div>
            )}
          </CardContent>
        </Card>
      ))}

      <Card className="border-[#8B5A96]/20 bg-[#8B5A96]/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-[#8B5A96]">
            <Shield className="h-5 w-5" />
            How Mobile Profiles Work
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div>
            <strong>1. Generate Profile:</strong> Create a secure mobile profile for your child's device
          </div>
          <div>
            <strong>2. Share Safely:</strong> Copy the download URL and share it with your child
          </div>
          <div>
            <strong>3. Transparent Setup:</strong> Your child sees clear explanations of all safety features
          </div>
          <div>
            <strong>4. Automatic Protection:</strong> Content filtering, educational promotion, and VPN blocking activate
          </div>
          <div>
            <strong>5. Ongoing Monitoring:</strong> Track usage with full transparency and compliance
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
