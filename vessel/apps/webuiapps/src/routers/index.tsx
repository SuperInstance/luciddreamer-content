import React, { lazy } from 'react';
import { RouteObject } from 'react-router-dom';

const Shell = lazy(() => import('@/components/Shell'));

// Vessel mode: Shell as root with desktop + floating windows
const rootRouter: RouteObject[] = [
  {
    path: '*',
    element: (
      <React.Suspense>
        <Shell />
      </React.Suspense>
    ),
  },
];

export default rootRouter;
