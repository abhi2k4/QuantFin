import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

export default function Terms() {
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
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </Link>
        
        <h1 className="text-5xl font-bold gradient-text mb-6">Terms of Service</h1>
        <p className="text-sm text-gray-500 mb-12">Last updated: October 10, 2025</p>
        
        <div className="card space-y-6">
          <p className="text-gray-400">
            Our terms of service are being finalized to ensure clarity and fairness for all users of QuantFin AI.
          </p>
          
          <div>
            <h2 className="text-2xl font-bold text-white mb-3">Key Terms</h2>
            <ul className="list-disc list-inside text-gray-400 space-y-2">
              <li>QuantFin AI is provided for informational purposes</li>
              <li>Investment decisions are your responsibility</li>
              <li>We do not provide financial advice</li>
              <li>Past performance does not guarantee future results</li>
            </ul>
          </div>
          
          <p className="text-gray-500 text-sm">
            Complete terms of service documentation coming soon.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
