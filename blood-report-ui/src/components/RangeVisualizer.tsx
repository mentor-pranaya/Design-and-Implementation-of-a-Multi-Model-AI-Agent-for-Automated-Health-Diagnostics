/**
 * Range Visualizer Component
 * Visual representation of parameter value within reference range
 */

import type { ReferenceRange } from '@/types/domain';

interface RangeVisualizerProps {
  value: number;
  referenceRange: ReferenceRange;
  unit: string;
  classification: string;
}

export default function RangeVisualizer({
  value,
  referenceRange,
  unit,
  classification,
}: RangeVisualizerProps) {
  const { min, max } = referenceRange;

  // Calculate position percentage
  const range = max - min;
  const valuePosition = ((value - min) / range) * 100;
  
  // Clamp position between 0 and 100
  const clampedPosition = Math.max(0, Math.min(100, valuePosition));

  // Determine if value is outside range
  const isLow = value < min;
  const isHigh = value > max;
  const isNormal = !isLow && !isHigh;

  // Get marker color based on classification
  const getMarkerColor = () => {
    switch (classification) {
      case 'High':
        return 'bg-red-600 border-red-700';
      case 'Low':
        return 'bg-orange-600 border-orange-700';
      case 'Normal':
        return 'bg-green-600 border-green-700';
      default:
        return 'bg-gray-600 border-gray-700';
    }
  };

  return (
    <div className="w-full">
      {/* Value Labels */}
      <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
        <span>{min} {unit}</span>
        <span className="font-medium">
          {value} {unit}
        </span>
        <span>{max} {unit}</span>
      </div>

      {/* Visual Range Bar */}
      <div className="relative h-8 bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden">
        {/* Normal Range (Green Zone) */}
        <div
          className="absolute h-full bg-green-100 dark:bg-green-900/30"
          style={{
            left: '0%',
            width: '100%',
          }}
        />

        {/* Range Boundaries */}
        <div className="absolute inset-0 flex items-center">
          {/* Left boundary */}
          <div className="absolute left-0 w-0.5 h-full bg-green-600 dark:bg-green-500" />
          
          {/* Right boundary */}
          <div className="absolute right-0 w-0.5 h-full bg-green-600 dark:bg-green-500" />
        </div>

        {/* Value Marker */}
        <div
          className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 transition-all duration-300"
          style={{ left: `${clampedPosition}%` }}
        >
          <div
            className={`w-4 h-4 rounded-full border-2 ${getMarkerColor()} shadow-lg`}
            title={`${value} ${unit}`}
          />
          {/* Marker Line */}
          <div
            className={`absolute top-1/2 left-1/2 -translate-x-1/2 w-0.5 h-8 ${
              classification === 'High' ? 'bg-red-600' :
              classification === 'Low' ? 'bg-orange-600' :
              'bg-green-600'
            }`}
          />
        </div>

        {/* Out of Range Indicators */}
        {isLow && (
          <div className="absolute left-0 top-0 bottom-0 w-1 bg-orange-600 dark:bg-orange-500" />
        )}
        {isHigh && (
          <div className="absolute right-0 top-0 bottom-0 w-1 bg-red-600 dark:bg-red-500" />
        )}
      </div>

      {/* Status Text */}
      <div className="mt-2 text-center">
        {isNormal && (
          <p className="text-sm text-green-600 dark:text-green-400">
            Within normal range
          </p>
        )}
        {isLow && (
          <p className="text-sm text-orange-600 dark:text-orange-400">
            Below normal range ({(min - value).toFixed(1)} {unit} below minimum)
          </p>
        )}
        {isHigh && (
          <p className="text-sm text-red-600 dark:text-red-400">
            Above normal range ({(value - max).toFixed(1)} {unit} above maximum)
          </p>
        )}
      </div>
    </div>
  );
}
