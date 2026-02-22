/**
 * Parameter Card Component
 * Displays a blood parameter with value, classification, and reference range
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { BloodParameter } from '@/types/domain';

interface ParameterCardProps {
  parameter: BloodParameter;
  showTrend?: boolean;
}

export default function ParameterCard({ parameter, showTrend = false }: ParameterCardProps) {
  const [expanded, setExpanded] = useState(false);

  // Get classification color
  const getClassificationColor = (classification: string) => {
    switch (classification) {
      case 'High':
        return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
      case 'Low':
        return 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800';
      case 'Normal':
        return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
      default:
        return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800';
    }
  };

  // Get trend icon
  const getTrendIcon = () => {
    if (!parameter.trend) return null;
    
    switch (parameter.trend) {
      case 'increasing':
        return <TrendingUp className="w-4 h-4" />;
      case 'decreasing':
        return <TrendingDown className="w-4 h-4" />;
      case 'stable':
        return <Minus className="w-4 h-4" />;
      default:
        return null;
    }
  };

  const classificationColor = getClassificationColor(parameter.classification);

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
      {/* Card Header */}
      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <h3 className="font-semibold text-gray-900 dark:text-white text-lg">
              {parameter.name}
            </h3>
            {parameter.category && (
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {parameter.category}
              </p>
            )}
          </div>
          
          {/* Classification Badge */}
          <span
            className={`px-3 py-1 rounded-full text-sm font-medium border ${classificationColor}`}
          >
            {parameter.classification}
          </span>
        </div>

        {/* Value Display */}
        <div className="flex items-baseline space-x-2 mb-3">
          <span className="text-3xl font-bold text-gray-900 dark:text-white">
            {parameter.value}
          </span>
          <span className="text-lg text-gray-600 dark:text-gray-400">
            {parameter.unit}
          </span>
          {showTrend && parameter.trend && (
            <div className="flex items-center space-x-1 text-gray-600 dark:text-gray-400">
              {getTrendIcon()}
              {parameter.percentChange !== undefined && (
                <span className="text-sm">
                  {parameter.percentChange > 0 ? '+' : ''}
                  {parameter.percentChange.toFixed(1)}%
                </span>
              )}
            </div>
          )}
        </div>

        {/* Reference Range */}
        <div className="text-sm text-gray-600 dark:text-gray-400">
          <span className="font-medium">Reference Range: </span>
          <span>
            {parameter.referenceRange.min} - {parameter.referenceRange.max} {parameter.referenceRange.unit}
          </span>
          {parameter.referenceRange.sex && parameter.referenceRange.sex !== 'All' && (
            <span className="ml-2">({parameter.referenceRange.sex})</span>
          )}
          {parameter.referenceRange.ageMin && parameter.referenceRange.ageMax && (
            <span className="ml-2">
              (Age {parameter.referenceRange.ageMin}-{parameter.referenceRange.ageMax})
            </span>
          )}
        </div>

        {/* Expand/Collapse Button */}
        {parameter.description && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="mt-3 flex items-center space-x-1 text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 transition-colors"
          >
            <span>{expanded ? 'Less details' : 'More details'}</span>
            {expanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        )}
      </div>

      {/* Expanded Details */}
      {expanded && parameter.description && (
        <div className="px-4 pb-4 pt-0 border-t border-gray-200 dark:border-gray-700">
          <div className="mt-3 text-sm text-gray-700 dark:text-gray-300">
            <p className="font-medium mb-1">About this parameter:</p>
            <p>{parameter.description}</p>
          </div>
          
          {parameter.previousValue !== undefined && (
            <div className="mt-3 text-sm text-gray-700 dark:text-gray-300">
              <p className="font-medium mb-1">Previous value:</p>
              <p>
                {parameter.previousValue} {parameter.unit}
                {parameter.percentChange !== undefined && (
                  <span className={parameter.percentChange > 0 ? 'text-red-600' : 'text-green-600'}>
                    {' '}({parameter.percentChange > 0 ? '+' : ''}
                    {parameter.percentChange.toFixed(1)}%)
                  </span>
                )}
              </p>
            </div>
          )}

          {parameter.referenceRange.context && (
            <div className="mt-3 text-sm text-gray-700 dark:text-gray-300">
              <p className="font-medium mb-1">Context:</p>
              <p>{parameter.referenceRange.context}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
