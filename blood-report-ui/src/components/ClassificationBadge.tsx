/**
 * Classification Badge Component
 * Displays classification status with icon and color coding
 */

import { CheckCircle, ArrowUp, ArrowDown, AlertCircle } from 'lucide-react';
import type { ClassificationType } from '@/types/domain';

interface ClassificationBadgeProps {
  classification: ClassificationType;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
  showLabel?: boolean;
}

export default function ClassificationBadge({
  classification,
  size = 'md',
  showIcon = true,
  showLabel = true,
}: ClassificationBadgeProps) {
  // Get icon based on classification
  const getIcon = () => {
    const iconSize = size === 'sm' ? 'w-4 h-4' : size === 'md' ? 'w-5 h-5' : 'w-6 h-6';
    
    switch (classification) {
      case 'Normal':
        return <CheckCircle className={iconSize} />;
      case 'High':
        return <ArrowUp className={iconSize} />;
      case 'Low':
        return <ArrowDown className={iconSize} />;
      default:
        return <AlertCircle className={iconSize} />;
    }
  };

  // Get color classes
  const getColorClasses = () => {
    switch (classification) {
      case 'Normal':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      case 'High':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'Low':
        return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  // Get size classes
  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-2 py-0.5 text-xs';
      case 'lg':
        return 'px-4 py-2 text-base';
      default:
        return 'px-3 py-1 text-sm';
    }
  };

  // Get explanation text
  const getExplanation = () => {
    switch (classification) {
      case 'Normal':
        return 'Value is within the normal reference range';
      case 'High':
        return 'Value is above the normal reference range';
      case 'Low':
        return 'Value is below the normal reference range';
      default:
        return 'Classification could not be determined';
    }
  };

  return (
    <div className="inline-flex flex-col items-start">
      <span
        className={`inline-flex items-center space-x-1.5 rounded-full font-medium border ${getColorClasses()} ${getSizeClasses()}`}
        title={getExplanation()}
      >
        {showIcon && getIcon()}
        {showLabel && <span>{classification}</span>}
      </span>
    </div>
  );
}
