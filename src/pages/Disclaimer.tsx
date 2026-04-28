import { motion } from 'framer-motion';
import { IconArrowLeft, IconAlertTriangle } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

export default function Disclaimer() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      className="min-h-screen"
    >
      <div className="container mx-auto px-6 py-24 max-w-4xl">
        <Link to="/">
          <Button className="btn-secondary mb-8 rounded-xl">
            <IconArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </Link>
        
        <div className="flex items-center gap-3 mb-6">
          <IconAlertTriangle className="w-10 h-10 text-yellow-400" />
          <h1 className="text-5xl font-bold gradient-text">Disclaimer</h1>
        </div>
        <p className="text-sm text-gray-500 mb-12">Last updated: October 10, 2025</p>
        
        <div className="card space-y-6">
          <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-xl">
            <p className="text-yellow-400 font-semibold">Important Investment Notice</p>
          </div>
          
          <p className="text-gray-400">
            QuantFin AI provides AI-powered portfolio analysis and predictions for informational and educational purposes only.
          </p>
          
          <div>
            <h2 className="text-2xl font-bold text-white mb-3">Key Points</h2>
            <ul className="list-disc list-inside text-gray-400 space-y-2">
              <li>Not financial advice - consult a licensed financial advisor</li>
              <li>Predictions do not guarantee future performance</li>
              <li>Stock market investments carry inherent risks</li>
              <li>Past performance is not indicative of future results</li>
              <li>You are solely responsible for your investment decisions</li>
            </ul>
          </div>
          
          <p className="text-gray-500 text-sm">
            Full disclaimer documentation coming soon.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
