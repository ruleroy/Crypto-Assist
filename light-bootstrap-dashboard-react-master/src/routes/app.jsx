import Dashboard from 'views/Dashboard/Dashboard';
import UserProfile from 'views/UserProfile/UserProfile';
import AnalyzeMarket from 'views/AnalyzeMarket/AnalyzeMarket';
import TableList from 'views/TableList/TableList';
import Typography from 'views/Typography/Typography';
import Icons from 'views/Icons/Icons';
import Maps from 'views/Maps/Maps';
import Notifications from 'views/Notifications/Notifications';
import Upgrade from 'views/Upgrade/Upgrade';

const appRoutes = [
    { path: "/dashboard", name: "Dashboard", icon: "pe-7s-graph", component: Dashboard },
    { path: "/analyze", name: "Analyze Market", icon: "pe-7s-graph3", component: AnalyzeMarket },
    { path: "/account", name: "Account", icon: "pe-7s-user", component: UserProfile },
    { redirect: true, path:"/", to:"/dashboard", name: "Dashboard" }
];

export default appRoutes;
