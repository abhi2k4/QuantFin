import { motion } from 'framer-motion';
import { IconArrowLeft } from '@tabler/icons-react';
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const fadeInUp = {
  hidden: { opacity: 0, y: 30 },
  visible: { opacity: 1, y: 0 }
};

export default function About() {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      className="min-h-screen"
    >
      <div className="container mx-auto px-6 py-24">
        <Link to="/">
          <Button className="btn-secondary mb-8 rounded-xl">
            <IconArrowLeft className="w-4 h-4 mr-2" />
            Back to Home
          </Button>
        </Link>
        
        <h1 className="text-5xl font-bold gradient-text mb-6">About Us</h1>
        <p className="text-xl text-gray-400 max-w-3xl">
          Learn more about QuantFin AI, our mission, and the team behind the platform.
        </p>
        
        <div className="mt-12 card">
          <p className="text-gray-400">
            This page is under construction. Our story and team information will be available soon.
          </p>
        </div>
      </div>
    </motion.div>
  );
}
