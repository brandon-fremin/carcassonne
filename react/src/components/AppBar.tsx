import * as React from 'react';
import AppBar from '@mui/material/AppBar';
import Box from '@mui/material/Box';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import MenuIcon from '@mui/icons-material/Menu';
import AccountCircle from '@mui/icons-material/AccountCircle';
import MenuItem from '@mui/material/MenuItem';
import Menu from '@mui/material/Menu';

export interface MenuOption {
  label: string;
  onClick: () => void;
}

export interface ProfileOption {
  label: string;
  onClick: () => void;
}

interface AppBarProps {
  title: string;
  menuOptions?: MenuOption[];
  profileOptions?: ProfileOption[];
}

export default function CustomAppBar({ title, menuOptions = [], profileOptions = [] }: AppBarProps) {
  const [menuAnchorEl, setMenuAnchorEl] = React.useState<null | HTMLElement>(null);
  const [profileAnchorEl, setProfileAnchorEl] = React.useState<null | HTMLElement>(null);

  const handleMenuClick = (event: React.MouseEvent<HTMLElement>) => {
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };

  const handleProfileClick = (event: React.MouseEvent<HTMLElement>) => {
    setProfileAnchorEl(event.currentTarget);
  };

  const handleProfileClose = () => {
    setProfileAnchorEl(null);
  };

  return (
    <AppBar position="static">
      <Toolbar>
        {menuOptions.length > 0 && (
          <>
            <IconButton
              size="large"
              edge="start"
              color="inherit"
              aria-label="menu"
              aria-controls="main-menu"
              aria-haspopup="true"
              onClick={handleMenuClick}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Menu
              id="main-menu"
              anchorEl={menuAnchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
              open={Boolean(menuAnchorEl)}
              onClose={handleMenuClose}
            >
              {menuOptions.map((option, index) => (
                <MenuItem
                  key={index}
                  onClick={() => {
                    option.onClick();
                    handleMenuClose();
                  }}
                >
                  {option.label}
                </MenuItem>
              ))}
            </Menu>
          </>
        )}
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          {title}
        </Typography>
        {profileOptions.length > 0 && (
          <div>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="profile-menu"
              aria-haspopup="true"
              onClick={handleProfileClick}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="profile-menu"
              anchorEl={profileAnchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(profileAnchorEl)}
              onClose={handleProfileClose}
            >
              {profileOptions.map((option, index) => (
                <MenuItem
                  key={index}
                  onClick={() => {
                    option.onClick();
                    handleProfileClose();
                  }}
                >
                  {option.label}
                </MenuItem>
              ))}
            </Menu>
          </div>
        )}
      </Toolbar>
    </AppBar>
  );
}