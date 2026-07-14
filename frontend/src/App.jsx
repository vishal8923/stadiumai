import React from 'react';
import { useAppStore } from '@/store/appStore';
import { AppLayout } from '@/components/layout/AppLayout';
import { ScreenTransition } from '@/components/layout/ScreenTransition';

// Screens
import { SplashScreen } from '@/components/screens/SplashScreen';
import { OnboardingScreen } from '@/components/screens/OnboardingScreen';
import { HomeScreen } from '@/components/screens/HomeScreen';
import { ChatScreen } from '@/components/screens/ChatScreen';
import { MapScreen } from '@/components/screens/MapScreen';
import { NavigationScreen } from '@/components/screens/NavigationScreen';
import { IncidentScreen } from '@/components/screens/IncidentScreen';
import { TransportScreen } from '@/components/screens/TransportScreen';
import { AccessibilityScreen } from '@/components/screens/AccessibilityScreen';
import { SustainabilityScreen } from '@/components/screens/SustainabilityScreen';
import { MatchScreen } from '@/components/screens/MatchScreen';
import { DashboardScreen } from '@/components/screens/DashboardScreen';
import { NotificationsScreen } from '@/components/screens/NotificationsScreen';

const ScreenRouter = () => {
  const currentScreen = useAppStore((s) => s.currentScreen);

  switch (currentScreen) {
    case 'splash':
      return <SplashScreen />;
    case 'onboarding':
      return <OnboardingScreen />;
    case 'home':
      return (
        <ScreenTransition screenKey="home">
          <HomeScreen />
        </ScreenTransition>
      );
    case 'chat':
      return (
        <ScreenTransition screenKey="chat">
          <ChatScreen />
        </ScreenTransition>
      );
    case 'map':
      return (
        <ScreenTransition screenKey="map">
          <MapScreen />
        </ScreenTransition>
      );
    case 'navigation':
      return (
        <ScreenTransition screenKey="navigation">
          <NavigationScreen />
        </ScreenTransition>
      );
    case 'incident':
      return (
        <ScreenTransition screenKey="incident">
          <IncidentScreen />
        </ScreenTransition>
      );
    case 'transport':
      return (
        <ScreenTransition screenKey="transport">
          <TransportScreen />
        </ScreenTransition>
      );
    case 'accessibility':
      return (
        <ScreenTransition screenKey="accessibility">
          <AccessibilityScreen />
        </ScreenTransition>
      );
    case 'sustainability':
      return (
        <ScreenTransition screenKey="sustainability">
          <SustainabilityScreen />
        </ScreenTransition>
      );
    case 'match':
      return (
        <ScreenTransition screenKey="match">
          <MatchScreen />
        </ScreenTransition>
      );
    case 'dashboard':
      return (
        <ScreenTransition screenKey="dashboard">
          <DashboardScreen />
        </ScreenTransition>
      );
    case 'notifications':
      return (
        <ScreenTransition screenKey="notifications">
          <NotificationsScreen />
        </ScreenTransition>
      );
    default:
      return (
        <ScreenTransition screenKey="home">
          <HomeScreen />
        </ScreenTransition>
      );
  }
};

function App() {
  return (
    <div className="app-container h-full w-full" style={{ background: '#0A1628' }}>
      <AppLayout>
        <ScreenRouter />
      </AppLayout>
    </div>
  );
}

export default App;
