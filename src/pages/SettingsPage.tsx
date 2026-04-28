import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { Separator } from '@/components/ui/separator';
import { IconBell, IconShield, IconDatabase, IconBolt } from '@tabler/icons-react';

export default function SettingsPage() {
  return (
    <>
      <div className="min-h-screen bg-[#0d0d0d] text-white">
        {/* Top Bar */}
        <div className="border-b border-[rgba(255,255,255,0.06)] bg-[rgba(13,13,13,0.9)] backdrop-blur-xl">
          <div className="max-w-[1600px] mx-auto px-6 py-4">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-bold">Settings</h1>
                <p className="text-sm text-gray-400 mt-1">Manage your account and preferences</p>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="max-w-[1600px] mx-auto px-6 py-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <Card className="p-6 bg-[#141414] border border-[rgba(255,255,255,0.07)]">
              <div className="space-y-6">
                {/* Notifications */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <IconBell className="w-5 h-5 text-cyan-400" />
                    <h3 className="font-semibold">Notifications</h3>
                  </div>
                  <div className="space-y-3">
                    {[
                      { label: 'Trading Signals', desc: 'Get notified of new trading opportunities' },
                      { label: 'Portfolio Updates', desc: 'Daily portfolio performance summaries' },
                      { label: 'Market Alerts', desc: 'Important market events and news' }
                    ].map((item, i) => (
                      <div key={i} className="flex items-center justify-between py-2">
                        <div>
                          <p className="font-medium">{item.label}</p>
                          <p className="text-sm text-gray-400">{item.desc}</p>
                        </div>
                        <Switch />
                      </div>
                    ))}
                  </div>
                </div>

                <Separator className="bg-white/10" />

                {/* Security */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <IconShield className="w-5 h-5 text-emerald-400" />
                    <h3 className="font-semibold">Security</h3>
                  </div>
                  <div className="space-y-3">
                    <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                      Change Password
                    </Button>
                    <Button variant="outline" className="w-full justify-start border-white/10 hover:bg-white/5">
                      Enable Two-Factor Authentication
                    </Button>
                  </div>
                </div>

                <Separator className="bg-white/10" />

                {/* Data & Performance */}
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <IconDatabase className="w-5 h-5 text-amber-400" />
                    <h3 className="font-semibold">Data & Performance</h3>
                  </div>
                  <div className="flex items-center justify-between py-2">
                    <div>
                      <p className="font-medium">GPU Acceleration</p>
                      <p className="text-sm text-gray-400">Use GPU for faster model training</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <IconBolt className="w-4 h-4 text-yellow-400" />
                      <Switch />
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </div>
    </>
  );
}
