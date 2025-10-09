import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

export default function Privacy() {
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
        
        <h1 className="text-5xl font-bold gradient-text mb-6">Privacy Policy</h1>
        <p className="text-sm text-gray-500 mb-12">Last updated: October 10, 2025</p>
        
        <div className="card space-y-6">
          <p className="text-gray-400">
            Our comprehensive privacy policy is being finalized. We take your privacy seriously and are committed to protecting your personal information.
          </p>
          
          <div>
            <h2 className="text-2xl font-bold text-white mb-3">Key Principles</h2>
            <ul className="list-disc list-inside text-gray-400 space-y-2">
              <li>We never sell your personal data</li>
              <li>Your portfolio information is encrypted and secure</li>
              <li>You have full control over your data</li>
              <li>We comply with all applicable data protection laws</li>
            </ul>
          </div>
          
          <p className="text-gray-500 text-sm">
            Full privacy policy documentation coming soon.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
