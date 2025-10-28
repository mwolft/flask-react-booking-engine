import { Outlet } from "react-router-dom/dist"
import ScrollToTop from "../components/ScrollToTop"
import { Navbar } from "../components/Navbar"
import { Footer } from "../components/Footer"
import 'bootstrap/dist/css/bootstrap.min.css';
import 'react-loading-skeleton/dist/skeleton.css';


export const Layout = () => {
    return (
        <div className="app-wrapper">
            <ScrollToTop>
                <Navbar />
                <main className="content-main"> 
                    <Outlet />
                </main>
            </ScrollToTop>
            <Footer />
        </div>
    )
}