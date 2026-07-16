import { Bell, ArrowLeft } from 'lucide-react';
import { useAppStore } from '@/store/appStore';
import { IconButton } from '@/components/ui/IconButton';

export const Header = ({ greeting = true, showBack = false, onBack }) => {
  const navigateTo = useAppStore((s) => s.navigateTo);
  const unreadCount = useAppStore((s) => s.unreadCount);

  return (
    <div className="flex items-center justify-between px-4 pt-4 pb-2">
      <div className="flex items-center gap-3">
        {showBack && (
          <button
            onClick={onBack}
            className="flex items-center justify-center w-10 h-10 rounded-full cursor-pointer"
            style={{
              background: '#111D2E',
              boxShadow: '4px 4px 8px #050A10, -4px -4px 8px #1A2A40',
            }}
          >
            <ArrowLeft size={20} color="#F0F4F8" />
          </button>
        )}
        {greeting && (
          <div>
            <h1 className="font-inter font-semibold text-h1 text-stadium-text">
              Good evening, Alex!
            </h1>
            <p className="font-inter text-body text-stadium-text-secondary mt-0.5">
              World Cup Final — 45 min to kickoff
            </p>
          </div>
        )}
      </div>
      <div className="flex items-center gap-3">
        <IconButton
          icon={<Bell size={20} color="#8B9DB8" />}
          onClick={() => navigateTo('notifications')}
          badge={unreadCount > 0 ? unreadCount : null}
          ariaLabel="Notifications"
        />
        <div
          className="flex items-center justify-center rounded-full overflow-hidden"
          style={{
            width: 48,
            height: 48,
            background: '#111D2E',
            boxShadow: '8px 8px 16px #050A10, -8px -8px 16px #1A2A40',
            border: '2px solid #FFD700',
          }}
        >
          <span className="text-lg font-bold text-stadium-text">A</span>
        </div>
      </div>
    </div>
  );
};
